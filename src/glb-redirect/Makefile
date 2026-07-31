KDIR?=/usr/src/linux-headers-$(shell uname -r)
BUILDDIR?=.

ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

DKMS_MOD_VER:=$(shell grep 'PACKAGE_VERSION' dkms.conf | cut -d'=' -f2)

obj-m += ipt_GLBREDIRECT.o

# Probe the kernel headers for the __cookie_v[46]_check() arity. Upstream
# removed the trailing 'cookie' argument in Linux 6.8, but distributions
# backport the change, so a LINUX_VERSION_CODE check in the C code is not
# reliable on its own. When we can read net/tcp.h we pass a definitive answer
# through to the C code; otherwise it falls back to a version heuristic. The
# 3-arg declaration carries a trailing 'u32 cookie' parameter (the only u32 in
# the prototype), so its presence distinguishes the two forms.
COOKIE_TCP_H := $(firstword $(wildcard $(srctree)/include/net/tcp.h $(srctree)/source/include/net/tcp.h))
ifneq ($(COOKIE_TCP_H),)
# Capture the __cookie_v4_check() declaration (it may span two lines). We only
# emit a define when the declaration is actually found; if a future header
# layout change hides it, COOKIE_DECL stays empty, no define is emitted, and the
# C code falls back to its LINUX_VERSION_CODE heuristic. The 3-arg form carries
# a trailing 'u32 cookie' parameter (the only u32 in the prototype), which
# distinguishes the two forms. NB: keep the awk free of parentheses and commas
# -- embedding either inside $(shell ...) breaks make's function/conditional
# parser.
COOKIE_DECL := $(shell awk '/__cookie_v4_check/{f=1} f{b=b $$0} f&&/;/{print b; exit}' $(COOKIE_TCP_H))
ifneq ($(COOKIE_DECL),)
ifeq ($(findstring u32,$(COOKIE_DECL)),)
ccflags-y += -DGLB_COOKIE_CHECK_NO_COOKIE_ARG
else
ccflags-y += -DGLB_COOKIE_CHECK_HAS_COOKIE_ARG
endif
endif
endif

# Probe the kernel headers for the socket-lookup helper arity. Upstream removed
# the 'struct inet_hashinfo *hashinfo' argument (callers no longer pass
# &tcp_hashinfo), but distributions may backport that change, so a
# LINUX_VERSION_CODE check in the C code is not reliable on its own. When we can
# read net/inet_hashtables.h we pass a definitive answer through to the C code;
# otherwise it falls back to a version heuristic. The old declaration carries a
# 'struct inet_hashinfo *hashinfo' parameter -- the presence of the 'inet_hashinfo'
# type name in the inet_lookup_established() declaration distinguishes the two
# forms. NB: as with the cookie probe above, keep the awk free of parentheses
# and commas -- embedding either inside $(shell ...) breaks make's
# function/conditional parser, so we terminate accumulation on the first ';'.
HASHINFO_INET_H := $(firstword $(wildcard $(srctree)/include/net/inet_hashtables.h $(srctree)/source/include/net/inet_hashtables.h))
ifneq ($(HASHINFO_INET_H),)
HASHINFO_DECL := $(shell awk '/inet_lookup_established/{f=1} f{b=b $$0} f&&/;/{print b; exit}' $(HASHINFO_INET_H))
ifneq ($(HASHINFO_DECL),)
ifeq ($(findstring inet_hashinfo,$(HASHINFO_DECL)),)
ccflags-y += -DGLB_INET_LOOKUP_NO_HASHINFO_ARG
else
ccflags-y += -DGLB_INET_LOOKUP_HAS_HASHINFO_ARG
endif
endif
endif

all: lib kmod

kmod:
	$(BUILD_VARS) make -C $(KDIR) M=$(ROOT_DIR) modules

clean:
	# we allow the following to fail since in our Docker build env we don't have a valid KDIR
	$(BUILD_VARS) make -C $(KDIR) M=$(ROOT_DIR) clean || true
	rm -rf libxt_GLBREDIRECT.so $(BUILDDIR)/glb-redirect-iptables-dkms_$(DKMS_MOD_VER)_*.deb

.PHONY: lib
lib: libxt_GLBREDIRECT.so

# Test/debug helper: echo the socket-lookup arity flag that the header probe
# above resolved (empty if it could not classify, in which case the C code
# falls back to a LINUX_VERSION_CODE heuristic). Exercised by
# script/test against fixture headers, so both detection
# branches are validated without needing a full kernel build. Point it at a
# fixture tree with `make srctree=<dir> print-lookup-arg`.
.PHONY: print-lookup-arg
print-lookup-arg:
	@echo "$(filter -DGLB_INET_LOOKUP_%,$(ccflags-y))"

.PHONY: install
install: lib kmod
	install -d $(DESTDIR)$(shell pkg-config --variable=xtlibdir xtables)
	install -m 0755 libxt_GLBREDIRECT.so $(DESTDIR)$(shell pkg-config --variable=xtlibdir xtables)
	install -d $(DESTDIR)/lib/modules/$(shell uname -r)/updates
	install ipt_GLBREDIRECT.ko $(DESTDIR)/lib/modules/$(shell uname -r)/updates

KSRC=/usr/src/linux-headers-$(shell uname -r)
IPT_CFLAGS=-DPIC -fPIC -Wno-cpp
IPT_LDFLAGS=-lxtables -shared

%.so: %.c
	$(CC) -o $@ $< $(IPT_CFLAGS) $(IPT_LDFLAGS)

mkdeb:
	rm -rf glb-redirect-iptables-dkms-mkdeb
	cp -R /etc/dkms/template-dkms-mkdeb/ glb-redirect-iptables-dkms-mkdeb
	chown : -R glb-redirect-iptables-dkms-mkdeb
	# Works around this bug: https://ubuntuforums.org/showthread.php?t=2234906
	sed -i '/chmod 644/d' glb-redirect-iptables-dkms-mkdeb/Makefile
	sed -i '/^Depends:/ s/$$/, pkg-config, libxtables12 | libxtables10, libxtables-dev | libxtables10/' glb-redirect-iptables-dkms-mkdeb/debian/control
	sed -i 's/^Maintainer: .*/Maintainer: GitHub <opensource+glb-director@github.com>/' glb-redirect-iptables-dkms-mkdeb/debian/control
	dkms mkdeb --source-only
	mv ../glb-redirect-iptables-dkms_$(DKMS_MOD_VER)_*.deb $(BUILDDIR)/
