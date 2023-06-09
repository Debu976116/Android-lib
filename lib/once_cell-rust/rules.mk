# Copyright (C) 2022 The Android Open Source Project
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

SRC_DIR = external/rust/crates/once_cell

MODULE_SRCS := $(SRC_DIR)/src/lib.rs

MODULE_CRATE_NAME := once_cell

MODULE_RUST_EDITION := 2018

MODULE_LIBRARY_DEPS += \
	trusty/user/base/lib/liballoc-rust \

MODULE_RUSTFLAGS += \
	--cfg 'feature="std"' \
	--cfg 'feature="alloc"' \
	--cfg 'feature="race"' \

include make/library.mk
