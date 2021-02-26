# Copyright (C) 2020 The Android Open Source Project
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

MANIFEST := $(LOCAL_DIR)/manifest.json

MODULE_SRCS += \
	$(LOCAL_DIR)/apploader.c \
	$(LOCAL_DIR)/apploader_package.c \

MODULE_DEPS += \
	trusty/user/base/lib/libc-trusty \
	trusty/user/base/lib/tipc \
	trusty/user/base/interface/apploader \

# Enabling APPLOADER_ALLOW_NS_CONNECT will allow apploader connections from the
# non-secure world.
APPLOADER_ALLOW_NS_CONNECT ?= false
ifeq (true,$(call TOBOOL,$(APPLOADER_ALLOW_NS_CONNECT)))
MODULE_COMPILEFLAGS += -DAPPLOADER_ALLOW_NS_CONNECT
endif

include make/module.mk
