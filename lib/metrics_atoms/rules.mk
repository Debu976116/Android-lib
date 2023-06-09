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

MODULE_PROTOC_PLUGIN := \
	trusty/host/common/scripts/metrics_atoms_protoc_plugin/metrics_atoms_protoc_plugin.py

MODULE_PROTO_PACKAGE := android/frameworks/stats

MODULE_PROTOS := \
	$(LOCAL_DIR)/$(MODULE_PROTO_PACKAGE)/atoms.proto

MODULE_LIBRARY_DEPS += \
	trusty/kernel/lib/shared/ibinder \
	trusty/user/base/lib/stats \

include make/protoc_plugin.mk
