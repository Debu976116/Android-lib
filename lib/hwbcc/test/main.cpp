/*
 * Copyright (C) 2021 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#define TLOG_TAG "hwbcc-test"

#include <cppbor.h>
#include <cppbor_parse.h>
#include <lib/hwbcc/client/hwbcc.h>
#include <lib/hwbcc/common/swbcc.h>
#include <openssl/curve25519.h>
#include <trusty_unittest.h>
#include <uapi/err.h>

#include <array>
#include <vector>

using PubKey = std::array<uint8_t, ED25519_PUBLIC_KEY_LEN>;

typedef struct {
    swbcc_session_t s;
} swbcc_t;

/* UUID of this test TA: {0e109d31-8bbe-47d6-bb47-e1dd08910e16} */
static const struct uuid self_uuid = {
        0x0e109d31,
        0x8bbe,
        0x47d6,
        {0xbb, 0x47, 0xe1, 0xdd, 0x08, 0x91, 0x0e, 0x16},
};

static const uint8_t test_mac_key[HWBCC_MAC_KEY_SIZE] = {
        0xf4, 0xe2, 0xd2, 0xbb, 0x2d, 0x07, 0x16, 0xb9, 0x66, 0x4b, 0x73,
        0xe8, 0x56, 0xd3, 0x6e, 0xfb, 0x08, 0xb4, 0x01, 0xd8, 0x86, 0x38,
        0xa7, 0x9a, 0x97, 0xb3, 0x98, 0x4f, 0x63, 0xdc, 0xef, 0xed};

static const uint8_t test_aad[] = {0xcf, 0xe1, 0x89, 0x39, 0xb1,
                                   0x72, 0xbf, 0x4f, 0xa8, 0x0f};

TEST_F_SETUP(swbcc) {
    _state->s = 0;
    int rc = swbcc_init(&_state->s, &self_uuid);
    ASSERT_EQ(rc, 0);

test_abort:;
}

TEST_F_TEARDOWN(swbcc) {
    swbcc_close(_state->s);
}

#define CHECK(statement)                                        \
    do {                                                        \
        if (!(statement)) {                                     \
            TLOGE("(" STRINGIFY(statement) ") check failed\n"); \
            return false;                                       \
        }                                                       \
    } while (0);

#define CHECK_NOT_NULL(val) CHECK(val != NULL)
#define CHECK_EQ(val1, val2) CHECK(val1 == val2)

static bool validate_pub_key_ed25519(const cppbor::Map* cose_key,
                                     PubKey* out_key) {
    /* This is what we expect. Note that field 4 is different in COSE spec.
     *  PubKeyEd25519 = {        // COSE_Key
     *      1 : 1,               // Key type : octet key pair
     *      3 : AlgorithmEdDSA,  // Algorithm : EdDSA
     *      4 : 2,               // Ops: Verify
     *      -1 : 6,              // Curve : Ed25519
     *      -2 : bstr            // X coordinate, little-endian
     *  }
     */
    const cppbor::Int* key_type = cose_key->get(1)->asInt();
    const cppbor::Int* algorithm = cose_key->get(3)->asInt();
    const cppbor::Int* curve = cose_key->get(-1)->asInt();
    const cppbor::Bstr* key = cose_key->get(-2)->asBstr();

    /*
     * TODO(b/201344393): There are inconsistencies in "ops" field depending on
     * implementation.
     *
     * const cppbor::Int* ops = cose_key->get(4)->asInt();
     * CHECK_NOT_NULL(ops);
     * CHECK_EQ(ops->value(), 2);
     */

    CHECK(cose_key->size() == 5);

    CHECK_NOT_NULL(key_type);
    CHECK_NOT_NULL(algorithm);
    CHECK_NOT_NULL(curve);
    CHECK_NOT_NULL(key);

    CHECK_EQ(key_type->value(), 1);
    CHECK_EQ(algorithm->value(), -8);
    CHECK_EQ(curve->value(), 6);
    CHECK_EQ(key->value().size(), ED25519_PUBLIC_KEY_LEN);

    std::copy(key->value().begin(), key->value().end(), out_key->begin());
    return true;
}

static bool validate_protected_params(const cppbor::Bstr* protected_params) {
    auto [parsed_params, _, err_msg] = cppbor::parse(protected_params);
    CHECK_NOT_NULL(parsed_params);

    const cppbor::Map* params = parsed_params->asMap();
    CHECK_NOT_NULL(params);

    CHECK_EQ(params->size(), 1);

    const cppbor::Int* algorithm = params->get(1)->asInt();
    CHECK_EQ(algorithm->value(), -8);

    return true;
}

static bool validate_subject_key(const cppbor::Bstr* subject_key,
                                 PubKey* out_key) {
    auto [parsed_subject_key, _, err_msg] = cppbor::parse(subject_key);
    CHECK_NOT_NULL(parsed_subject_key);

    const cppbor::Map* cose_key = parsed_subject_key->asMap();
    CHECK_NOT_NULL(cose_key);

    CHECK(validate_pub_key_ed25519(cose_key, out_key));

    return true;
}

static bool validate_bcc_payload(const cppbor::Bstr* bcc_payload,
                                 PubKey* out_key) {
    /* This is what we expect:
     *  BccPayload = {                          // CWT
     *      1 : tstr,                           // Issuer
     *      2 : tstr,                           // Subject
     *      // See the Open Profile for DICE for details on these fields.
     *      ? -4670545 : bstr,                  // Code Hash
     *      ? -4670546 : bstr,                  // Code Descriptor
     *      ? -4670547 : bstr,                  // Configuration Hash
     *      ? -4670548 : bstr .cbor {           // Configuration Descriptor
     *          ? -70002 : tstr,                // Component name
     *          ? -70003 : int,                 // Firmware version
     *          ? -70004 : null,                // Resettable
     *      },
     *      ? -4670549 : bstr,                  // Authority Hash
     *      ? -4670550 : bstr,                  // Authority Descriptor
     *      ? -4670551 : bstr,                  // Mode
     *      -4670552 : bstr .cbor PubKeyEd25519 // Subject Public Key
     *      -4670553 : bstr                     // Key Usage
     *  }
     */
    auto [parsed_payload, _, err_msg] = cppbor::parse(bcc_payload);
    CHECK_NOT_NULL(parsed_payload);

    const cppbor::Map* payload = parsed_payload->asMap();
    CHECK_NOT_NULL(payload);

    CHECK(payload->size() >= 4);

    const cppbor::Tstr* issuer = payload->get(1)->asTstr();
    const cppbor::Tstr* subject = payload->get(2)->asTstr();
    const cppbor::Bstr* subject_key = payload->get(-4670552)->asBstr();
    const cppbor::Bstr* key_usage = payload->get(-4670553)->asBstr();

    CHECK_NOT_NULL(issuer);
    CHECK_NOT_NULL(subject);
    CHECK_NOT_NULL(subject_key);
    CHECK_NOT_NULL(key_usage);

    CHECK(validate_subject_key(subject_key, out_key));

    return true;
}

static bool validate_bcc_entry(const cppbor::Array* bcc_entry,
                               const PubKey& prev_key,
                               PubKey* out_key) {
    /* This is what we expect:
     *  BccEntry = [                 // COSE_Sign1 (untagged)
     *      protected : bstr .cbor {
     *          1 : AlgorithmEdDSA,  // Algorithm
     *      },
     *      unprotected: {},
     *      payload: bstr .cbor BccPayload,
     *      signature: bstr .cbor PureEd25519(SigningKey,
     *                                        bstr .cbor BccEntryInput)
     *  ]
     *
     *  BccEntryInput = [
     *      context: "Signature1",
     *      protected: bstr .cbor {
     *          1 : AlgorithmEdDSA,  // Algorithm
     *      },
     *      external_aad: bstr .size 0,
     *      payload: bstr .cbor BccPayload
     *  ]
     */
    const cppbor::Bstr* protected_params = bcc_entry->get(0)->asBstr();
    const cppbor::Map* unprotected_params = bcc_entry->get(1)->asMap();
    const cppbor::Bstr* payload = bcc_entry->get(2)->asBstr();
    const cppbor::Bstr* signature = bcc_entry->get(3)->asBstr();

    CHECK_EQ(bcc_entry->size(), 4);

    CHECK_NOT_NULL(protected_params);
    CHECK_NOT_NULL(unprotected_params);
    CHECK_NOT_NULL(payload);
    CHECK_NOT_NULL(signature);

    CHECK(validate_protected_params(protected_params));
    CHECK_EQ(unprotected_params->size(), 0);
    CHECK(validate_bcc_payload(payload, out_key));

    std::vector<uint8_t> signature_input = cppbor::Array()
                                                   .add("Signature1")
                                                   .add(*protected_params)
                                                   .add(cppbor::Bstr())
                                                   .add(*payload)
                                                   .encode();

    int rc = ED25519_verify(signature_input.data(), signature_input.size(),
                            signature->value().data(), prev_key.data());
    CHECK_EQ(rc, 1);

    return true;
}

/* TODO: Also validate non-degenerate BCC case */
static bool validate_bcc(const uint8_t* bcc,
                         size_t bcc_size,
                         std::vector<PubKey>* keys) {
    /* This is what we expect:
     *  Bcc = [
     *      PubKeyEd25519, // DK_pub
     *      + BccEntry,    // Root -> leaf (KM_pub)
     *  ]
     */
    auto [parsed_bcc, _, err_msg] = cppbor::parse(bcc, bcc_size);
    CHECK_NOT_NULL(parsed_bcc);

    const cppbor::Array* bcc_array = parsed_bcc->asArray();
    CHECK_NOT_NULL(bcc_array);

    CHECK_EQ(bcc_array->size(), 2);

    const cppbor::Map* dk_pub = bcc_array->get(0)->asMap();
    const cppbor::Array* bcc_entry = bcc_array->get(1)->asArray();

    CHECK_NOT_NULL(dk_pub);
    CHECK_NOT_NULL(bcc_entry);

    PubKey dk_pub_key;
    PubKey km_pub_key;

    CHECK(validate_pub_key_ed25519(dk_pub, &dk_pub_key));
    CHECK(validate_bcc_entry(bcc_entry, dk_pub_key, &km_pub_key));

    keys->push_back(dk_pub_key);
    keys->push_back(km_pub_key);

    return true;
}

TEST_F(swbcc, mac) {
    int rc;
    uint8_t cose_sign1[HWBCC_MAX_RESP_PAYLOAD_SIZE];
    size_t cose_sign1_size = 0;

    memset(cose_sign1, 0, sizeof(cose_sign1));

    rc = swbcc_sign_mac(_state->s, true, HWBCC_ALGORITHM_ED25519, test_mac_key,
                        test_aad, sizeof(test_aad), cose_sign1,
                        sizeof(cose_sign1), &cose_sign1_size);
    ASSERT_EQ(rc, 0);

    ASSERT_GT(cose_sign1_size, 0);
    /* TODO: Check contents of cose_sign1. */

test_abort:;
}

TEST_F(swbcc, bcc) {
    int rc;
    uint8_t bcc[HWBCC_MAX_RESP_PAYLOAD_SIZE];
    size_t bcc_size = 0;
    std::vector<PubKey> keys;
    uint8_t* dk_pub_key;
    uint8_t* km_pub_key;

    memset(bcc, 0, sizeof(bcc));

    rc = swbcc_get_bcc(_state->s, true, bcc, sizeof(bcc), &bcc_size);
    ASSERT_EQ(rc, 0);
    ASSERT_GT(bcc_size, 0);

    ASSERT_EQ(validate_bcc(bcc, bcc_size, &keys), true);

    /* Only a degenerate self-signed BCC is currently supported. */
    ASSERT_EQ(keys.size(), 2);

    dk_pub_key = keys[0].data();
    km_pub_key = keys[1].data();
    ASSERT_EQ(memcmp(dk_pub_key, km_pub_key, ED25519_PUBLIC_KEY_LEN), 0);

test_abort:;
}

/* Check that test mode yields different output every time */
TEST(hwbcc, protected_data_test_mode) {
    int rc;
    uint8_t cose_sign1[HWBCC_MAX_RESP_PAYLOAD_SIZE];
    size_t cose_sign1_size;
    uint8_t bcc[HWBCC_MAX_RESP_PAYLOAD_SIZE];
    size_t bcc_size;
    std::vector<PubKey> keys1;
    std::vector<PubKey> keys2;

    /* Get first set of keys */
    memset(cose_sign1, 0, sizeof(cose_sign1));
    memset(bcc, 0, sizeof(bcc));

    rc = hwbcc_get_protected_data(true, HWBCC_ALGORITHM_ED25519, test_mac_key,
                                  test_aad, sizeof(test_aad), cose_sign1,
                                  sizeof(cose_sign1), &cose_sign1_size, bcc,
                                  sizeof(bcc), &bcc_size);
    ASSERT_EQ(rc, 0);

    ASSERT_GT(cose_sign1_size, 0);
    ASSERT_GT(bcc_size, 0);

    ASSERT_EQ(validate_bcc(bcc, bcc_size, &keys1), true);

    /* Get second set of keys */
    memset(cose_sign1, 0, sizeof(cose_sign1));
    memset(bcc, 0, sizeof(bcc));

    rc = hwbcc_get_protected_data(true, HWBCC_ALGORITHM_ED25519, test_mac_key,
                                  test_aad, sizeof(test_aad), cose_sign1,
                                  sizeof(cose_sign1), &cose_sign1_size, bcc,
                                  sizeof(bcc), &bcc_size);
    ASSERT_EQ(rc, 0);

    ASSERT_GT(cose_sign1_size, 0);
    ASSERT_GT(bcc_size, 0);

    ASSERT_EQ(validate_bcc(bcc, bcc_size, &keys2), true);

    /* The two sets of keys must be different in test mode. */
    ASSERT_NE(memcmp(keys1[0].data(), keys2[0].data(), ED25519_PUBLIC_KEY_LEN),
              0);
    ASSERT_NE(memcmp(keys1[1].data(), keys2[1].data(), ED25519_PUBLIC_KEY_LEN),
              0);

test_abort:;
}

/*
 * Macro to enable test cases for generic ARM64 platform only.
 * (This includes generic_arm32 targets too).
 */
#if defined(PLATFORM_GENERIC_ARM64)
#define GENERIC_ARM64_PLATFORM_ONLY_TEST(name) name
#else
#define GENERIC_ARM64_PLATFORM_ONLY_TEST(name) DISABLED_##name
#endif

/*
 * Device key is hard-coded on emulator targets, i.e. BCC keys are fixed too.
 * We test that BCC keys don't change to make sure that we don't accidentally
 * change the key derivation procedure.
 */
static const uint8_t emulator_pub_key[ED25519_PUBLIC_KEY_LEN] = {
        0xc0, 0xdd, 0x6c, 0xf4, 0x3e, 0x66, 0x15, 0xc7, 0x4d, 0x23, 0xb8,
        0x96, 0x11, 0x11, 0xc9, 0x88, 0x07, 0x92, 0x2c, 0x8f, 0x32, 0xf6,
        0x79, 0x85, 0x86, 0x36, 0xad, 0xbd, 0x20, 0xf0, 0x9b, 0x21};

TEST(hwbcc, GENERIC_ARM64_PLATFORM_ONLY_TEST(protected_data)) {
    int rc;
    uint8_t cose_sign1[HWBCC_MAX_RESP_PAYLOAD_SIZE];
    size_t cose_sign1_size;
    uint8_t bcc[HWBCC_MAX_RESP_PAYLOAD_SIZE];
    size_t bcc_size;
    std::vector<PubKey> keys;
    uint8_t* dk_pub_key;
    uint8_t* km_pub_key;

    memset(cose_sign1, 0, sizeof(cose_sign1));
    memset(bcc, 0, sizeof(bcc));

    rc = hwbcc_get_protected_data(false, HWBCC_ALGORITHM_ED25519, test_mac_key,
                                  test_aad, sizeof(test_aad), cose_sign1,
                                  sizeof(cose_sign1), &cose_sign1_size, bcc,
                                  sizeof(bcc), &bcc_size);
    ASSERT_EQ(rc, 0);

    ASSERT_GT(cose_sign1_size, 0);
    ASSERT_GT(bcc_size, 0);

    ASSERT_EQ(validate_bcc(bcc, bcc_size, &keys), true);
    ASSERT_EQ(keys.size(), 2);

    dk_pub_key = keys[0].data();
    km_pub_key = keys[1].data();
    ASSERT_EQ(memcmp(emulator_pub_key, dk_pub_key, ED25519_PUBLIC_KEY_LEN), 0);
    ASSERT_EQ(memcmp(dk_pub_key, km_pub_key, ED25519_PUBLIC_KEY_LEN), 0);

test_abort:;
}

PORT_TEST(hwbcc, "com.android.trusty.hwbcc.test");
