/*
 * Copyright (C) 2019 The Android Open Source Project
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

#pragma once

#include <gtest/gtest.h>
#include <lib/unittest/unittest.h>
#include <lk/compiler.h>

#define PORT_GTEST(suite_name, port_name_string)          \
    __BEGIN_CDECLS                                        \
    static bool run_##suite_name(struct unittest* test) { \
        return RUN_ALL_TESTS() == 0;                      \
    }                                                     \
                                                          \
    int main(int argc, char** argv) {                     \
        static struct unittest test = {                   \
                .port_name = port_name_string,            \
                .run_test = run_##suite_name,             \
        };                                                \
        struct unittest* tests = &test;                   \
        /* gtest requires argc > 1 */                     \
        int fake_argc = 1;                                \
        char* fake_argv[] = {(char*)"test", NULL};        \
        testing::InitGoogleTest(&fake_argc, fake_argv);   \
        return unittest_main(&tests, 1);                  \
    }                                                     \
    __END_CDECLS
