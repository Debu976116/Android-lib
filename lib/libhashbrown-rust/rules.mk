# Copyright (C) 2021 The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

LOCAL_DIR := $(GET_LOCAL_DIR)

MODULE := $(LOCAL_DIR)

HASHBROWN_DIR = $(RUST_BINDIR)/../src/stdlibs/vendor/hashbrown

MODULE_SRCS := $(HASHBROWN_DIR)/src/lib.rs

MODULE_CRATE_NAME := hashbrown

MODULE_RUST_EDITION := 2021

MODULE_ADD_IMPLICIT_DEPS := false

MODULE_RUSTFLAGS += \
	--cfg 'feature="rustc-dep-of-std"' \
	--cfg 'feature="nightly"' \
	--cfg 'feature="rustc-internal-api"' \

# Suppress warnings since the crate generates warnings when being built as a
# dependency of std. We use `--cap-lints=allow` because that's done when
# building dependencies for rustc.
MODULE_RUSTFLAGS += \
	--cap-lints=allow \

MODULE_LIBRARY_DEPS += \
	trusty/user/base/lib/libcore-rust \
	trusty/user/base/lib/liballoc-rust \
	trusty/user/base/lib/libcompiler_builtins-rust \

include make/library.mk
