ifeq ($(call TOBOOL,$(MODULE_ADD_IMPLICIT_DEPS)),true)
MODULE_LIBRARY_DEPS += trusty/user/base/lib/libc-trusty
endif

# Remaining flags only apply to the trusty userspace, not the test-runner, which
# is also built with the library system.
ifeq (true,$(call TOBOOL,$(TRUSTY_USERSPACE)))

# If ASLR is disabled, don't make PIEs, it burns space
ifneq ($(ASLR), false)
    # Generate PIE code to allow ASLR to be applied
    MODULE_COMPILEFLAGS += -fPIC
endif

# LTO
ifneq (true,$(call TOBOOL,$(MODULE_DISABLE_LTO)))
ifeq (true,$(call TOBOOL,$(USER_LTO_ENABLED)))
MODULE_COMPILEFLAGS += -fvisibility=hidden -flto=thin
endif

# CFI
MODULE_CFI_ENABLED := false
ifneq (true,$(call TOBOOL,$(MODULE_DISABLE_CFI)))
ifeq (true,$(call TOBOOL,$(CFI_ENABLED)))
MODULE_CFI_ENABLED := true
endif

ifdef USER_CFI_ENABLED
MODULE_CFI_ENABLED := $(call TOBOOL,$(USER_CFI_ENABLED))
endif
endif # !MODULE_DISABLE_CFI

ifeq (true,$(call TOBOOL,$(MODULE_CFI_ENABLED)))
MODULE_COMPILEFLAGS += \
	-fsanitize-blacklist=trusty/kernel/lib/ubsan/exemptlist \
	-fsanitize=cfi \
	-DCFI_ENABLED
MODULE_LIBRARY_DEPS += trusty/kernel/lib/ubsan

ifeq (true,$(call TOBOOL,$(CFI_DIAGNOSTICS)))
MODULE_COMPILEFLAGS += -fno-sanitize-trap=cfi
endif
endif # MODULE_CFI_ENABLED

endif # !MODULE_DISABLE_LTO

# Stack protector
ifneq (true,$(call TOBOOL,$(MODULE_DISABLE_STACK_PROTECTOR)))
ifeq (true,$(call TOBOOL,$(USER_STACK_PROTECTOR)))
MODULE_COMPILEFLAGS += -fstack-protector-strong
endif
else
MODULE_COMPILEFLAGS += -fno-stack-protector
endif

# Shadow call stack
ifeq (true,$(call TOBOOL,$(SCS_ENABLED)))
# set in arch/$(ARCH)/toolchain.mk iff shadow call stack is supported
ifeq (false,$(call TOBOOL,$(ARCH_$(ARCH)_SUPPORTS_SCS)))
$(error Error: Shadow call stack is not supported for $(ARCH))
endif

ifeq (false,$(call TOBOOL,$(MODULE_DISABLE_SCS)))
# architectures that support SCS should set the flag that reserves
# a register for the shadow call stack in their toolchain.mk file
MODULE_COMPILEFLAGS += \
	-fsanitize=shadow-call-stack \

endif
endif # SCS_ENABLED

# Code coverage
ifeq (true,$(call TOBOOL,$(USER_COVERAGE_ENABLED)))
ifeq (false,$(call TOBOOL, $(MODULE_DISABLE_COVERAGE)))
MODULE_LIBRARY_DEPS += trusty/user/base/lib/sancov

# -fno-optimize-sibling-calls is necessary to get correct caller information in
# the sancov instrumentation.
MODULE_COMPILEFLAGS += \
	-fsanitize-coverage-blocklist=trusty/user/base/lib/sancov/exemptlist \
	-fsanitize-coverage=trace-pc-guard \
	-fno-optimize-sibling-calls

endif
endif

# HWASan
ifeq (true,$(call TOBOOL,$(USER_HWASAN_ENABLED)))
MODULE_DEFINES += \
	HWASAN_ENABLED=1 \
	HWASAN_SHADOW_SCALE=4 \

MODULE_LIBRARY_DEPS += trusty/user/base/lib/hwasan
MODULE_COMPILEFLAGS += \
	-fsanitize-blacklist=trusty/user/base/lib/hwasan/exemptlist \
	-fsanitize=hwaddress \
	-mllvm -hwasan-with-tls=0 \
	-mllvm -hwasan-globals=0 \
	-mllvm -hwasan-use-short-granules=0 \

endif

MODULE_DEFINES += TRUSTY_USERSPACE=1

endif # TRUSTY_USERSPACE

MODULE_CFI_ENABLED :=
MODULE_DISABLE_CFI :=
MODULE_DISABLE_COVERAGE :=
MODULE_DISABLE_LTO :=
MODULE_DISABLE_SCS :=
MODULE_DISABLE_STACK_PROTECTOR :=