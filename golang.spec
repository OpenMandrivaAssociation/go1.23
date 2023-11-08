%define _duplicate_files_terminate_build   0

%bcond_with bootstrap
# temporalily ignore test failures
%ifarch %{x86_64} %{ix86} aarch64 %{arm}
%bcond_without ignore_tests
%else
%bcond_with ignore_tests
%endif

# build ids are not currently generated:
# https://code.google.com/p/go/issues/detail?id=5238
#
# also, debuginfo extraction currently fails with
# "Failed to write file: invalid section alignment"
%global debug_package %{nil}

# we are shipping the full contents of src in the data subpackage, which
# contains binary-like things (ELF data for tests, etc)
%global _binaries_in_noarch_packages_terminate_build 0

# Do not check any files in doc or src for requires
%global __requires_exclude_from ^(%{_datadir}|/usr/lib)/%{name}/(doc|src)/.*$
# Seems to be the result of the shell parser screwing up on something
# in -src
%global __requires_exclude ^/bin/rc$

# Don't alter timestamps of especially the .a files (or else go will rebuild later)
# Actually, don't strip at all since we are not even building debug packages and this corrupts the dwarf testdata
%global __strip /bin/true

# rpmbuild magic to keep from having meta dependency on libc.so.6
#define _use_internal_dependency_generator 0
%define __find_requires %{nil}
%global __spec_install_post /usr/lib/rpm/check-rpaths   /usr/lib/rpm/check-buildroot  \
  /usr/lib/rpm/brp-compress

%global golibdir %{_libdir}/golang

# Golang build options.

# Build golang using external/internal(close to cgo disabled) linking.
%ifarch %{ix86} %{x86_64} ppc64le %{arm} aarch64 s390x
%global external_linker 1
%else
%global external_linker 0
%endif

# Build golang with cgo enabled/disabled(later equals more or less to internal linking).
%ifarch %{ix86} %{x86_64} ppc64le %{armx} s390x
%global cgo_enabled 1
%else
%global cgo_enabled 0
%endif

# Use golang/gcc-go as bootstrap compiler
%if %{with bootstrap}
%global golang_bootstrap 0
%global __cc /usr/bin/gcc
%global __cxx /usr/bin/g++
%else
%global golang_bootstrap 1
%endif

# Controls what ever we fail on failed tests
%if %{with ignore_tests}
%global fail_on_tests 0
%else
%global fail_on_tests 1
%endif

# Build golang shared objects for stdlib
%ifarch %{ix86} %{x86_64} ppc64le %{arm} aarch64
%global shared 1
%else
%global shared 0
%endif

# OpenMandriva GOROOT
%global goroot          %{_prefix}/lib/%{name}

%ifarch %{x86_64}
%global gohostarch  amd64
%endif
%ifarch %{ix86}
%global gohostarch  386
%endif
%ifarch %{arm}
%global gohostarch  arm
%endif
%ifarch aarch64
%global gohostarch  arm64
%endif
%ifarch ppc64
%global gohostarch  ppc64
%endif
%ifarch ppc64le
%global gohostarch  ppc64le
%endif
%ifarch s390x
%global gohostarch  s390x
%endif
%ifarch riscv64
%global gohostarch  riscv64
%endif

%global go_api %(echo %{version}|cut -d. -f1.2)

Name:           golang
Version:        1.21.4
Release:        1
Summary:        The Go Programming Language
# source tree includes several copies of Mark.Twain-Tom.Sawyer.txt under Public Domain
License:        BSD and Public Domain
URL:            http://golang.org/
Source0:        https://storage.googleapis.com/golang/go%{version}.src.tar.gz
# make possible to override default traceback level at build time by setting build tag rpm_crashtraceback
Source1:        fedora.go

# The compiler is written in Go. Needs go(1.4+) compiler for build.
%if !%{golang_bootstrap}
BuildRequires:  gcc-go >= 5
%else
BuildRequires:  golang > 1.4
%endif
BuildRequires:  hostname
BuildRequires:	locales-en >= 2.35-9
# for tests
BuildRequires:  pcre-devel
BuildRequires:  glibc-static-devel
BuildRequires:  perl-interpreter
BuildRequires:  procps-ng
BuildRequires:  timezone

Provides:       go = %{version}-%{release}

# Bundled/Vendored provides generated by
# go list -f {{.ImportPath}} ./src/vendor/... | sed "s:_$PWD/src/vendor/::g;s:_:.:;s:.*:Provides\: bundled(golang(&)):" && go list -f {{.ImportPath}} ./src/cmd/vendor/... | sed "s:_$PWD/src/cmd/vendor/::g;s:_:.:;s:.*:Provides\: bundled(golang(&)):"
Provides: bundled(golang(golang.org/x/crypto/chacha20poly1305))
Provides: bundled(golang(golang.org/x/crypto/cryptobyte))
Provides: bundled(golang(golang.org/x/crypto/cryptobyte/asn1))
Provides: bundled(golang(golang.org/x/crypto/curve25519))
Provides: bundled(golang(golang.org/x/crypto/internal/chacha20))
Provides: bundled(golang(golang.org/x/crypto/poly1305))
Provides: bundled(golang(golang.org/x/net/dns/dnsmessage))
Provides: bundled(golang(golang.org/x/net/http/httpguts))
Provides: bundled(golang(golang.org/x/net/http/httpproxy))
Provides: bundled(golang(golang.org/x/net/http2/hpack))
Provides: bundled(golang(golang.org/x/net/idna))
Provides: bundled(golang(golang.org/x/net/internal/nettest))
Provides: bundled(golang(golang.org/x/net/nettest))
Provides: bundled(golang(golang.org/x/text/secure))
Provides: bundled(golang(golang.org/x/text/secure/bidirule))
Provides: bundled(golang(golang.org/x/text/transform))
Provides: bundled(golang(golang.org/x/text/unicode))
Provides: bundled(golang(golang.org/x/text/unicode/bidi))
Provides: bundled(golang(golang.org/x/text/unicode/norm))
Provides: bundled(golang(github.com/google/pprof/driver))
Provides: bundled(golang(github.com/google/pprof/internal/binutils))
Provides: bundled(golang(github.com/google/pprof/internal/driver))
Provides: bundled(golang(github.com/google/pprof/internal/elfexec))
Provides: bundled(golang(github.com/google/pprof/internal/graph))
Provides: bundled(golang(github.com/google/pprof/internal/measurement))
Provides: bundled(golang(github.com/google/pprof/internal/plugin))
Provides: bundled(golang(github.com/google/pprof/internal/proftest))
Provides: bundled(golang(github.com/google/pprof/internal/report))
Provides: bundled(golang(github.com/google/pprof/internal/symbolizer))
Provides: bundled(golang(github.com/google/pprof/internal/symbolz))
Provides: bundled(golang(github.com/google/pprof/profile))
Provides: bundled(golang(github.com/google/pprof/third.party/d3))
Provides: bundled(golang(github.com/google/pprof/third.party/d3flamegraph))
Provides: bundled(golang(github.com/google/pprof/third.party/svgpan))
Provides: bundled(golang(github.com/ianlancetaylor/demangle))
Provides: bundled(golang(golang.org/x/arch/arm/armasm))
Provides: bundled(golang(golang.org/x/arch/arm64/arm64asm))
Provides: bundled(golang(golang.org/x/arch/ppc64/ppc64asm))
Provides: bundled(golang(golang.org/x/arch/x86/x86asm))
Provides: bundled(golang(golang.org/x/crypto/ssh/terminal))
Provides: bundled(golang(golang.org/x/sys/unix))
Provides: bundled(golang(golang.org/x/sys/windows))
Provides: bundled(golang(golang.org/x/sys/windows/registry))

Requires:       %{name}-bin = %{version}-%{release}
Requires:       %{name}-src = %{version}-%{release}
Requires:       go-srpm-macros

Patch:		https://src.fedoraproject.org/rpms/golang/raw/rawhide/f/0001-Modify-go.env.patch

# We no longer ship gold
Patch100:	go-no-ld.gold.patch

# Having documentation separate was broken
Obsoletes:      %{name}-docs < 1.1-4

# RPM can't handle symlink -> dir with subpackages, so merge back
Obsoletes:      %{name}-data < 1.1.1-4

# go1.4 deprecates a few packages
Obsoletes:      %{name}-vim < 1.4
Obsoletes:      emacs-%{name} < 1.4

Source100:      golang-gdbinit

%description
%{summary}.

%package       docs
Summary:       Golang compiler docs
Requires:      %{name} = %{version}-%{release}
BuildArch:     noarch
Obsoletes:     %{name}-docs < 1.1-4

%description   docs
%{summary}.

%package       misc
Summary:       Golang compiler miscellaneous sources
Requires:      %{name} = %{version}-%{release}
BuildArch:     noarch

%description   misc
%{summary}.

%package       tests
Summary:       Golang compiler tests for stdlib
Requires:      %{name} = %{version}-%{release}
BuildArch:     noarch

%description   tests
%{summary}.

%package        src
Summary:        Golang compiler source tree
BuildArch:      noarch
%description    src
%{summary}

%package        bin
Summary:        Golang core compiler tools
Requires:       go = %{version}-%{release}
# Pre-go1.5, all arches had to be bootstrapped individually, before usable, and
# env variables to compile for the target os-arch.
# Now the host compiler needs only the GOOS and GOARCH environment variables
# set to compile for the target os-arch.
Obsoletes:      %{name}-pkg-bin-linux-386 < 1.4.99
Obsoletes:      %{name}-pkg-bin-linux-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-bin-linux-arm < 1.4.99
Obsoletes:      %{name}-pkg-linux-386 < 1.4.99
Obsoletes:      %{name}-pkg-linux-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-linux-arm < 1.4.99
Obsoletes:      %{name}-pkg-darwin-386 < 1.4.99
Obsoletes:      %{name}-pkg-darwin-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-windows-386 < 1.4.99
Obsoletes:      %{name}-pkg-windows-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-plan9-386 < 1.4.99
Obsoletes:      %{name}-pkg-plan9-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-freebsd-386 < 1.4.99
Obsoletes:      %{name}-pkg-freebsd-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-freebsd-arm < 1.4.99
Obsoletes:      %{name}-pkg-netbsd-386 < 1.4.99
Obsoletes:      %{name}-pkg-netbsd-amd64 < 1.4.99
Obsoletes:      %{name}-pkg-netbsd-arm < 1.4.99
Obsoletes:      %{name}-pkg-openbsd-386 < 1.4.99
Obsoletes:      %{name}-pkg-openbsd-amd64 < 1.4.99

Obsoletes:      golang-vet < 0-12.1
Obsoletes:      golang-cover < 0-12.1

# We strip the meta dependency, but go does require glibc.
# This is an odd issue, still looking for a better fix.
Requires:       glibc
Requires:       %{__cc}
Requires:       git
Requires:       subversion
Requires:       mercurial

%description    bin
%{summary}.

# Workaround old RPM bug of symlink-replaced-with-dir failure
%pretrans -p <lua>
for _,d in pairs({"api", "doc", "include", "lib", "src"}) do
  path = "%{goroot}/" .. d
  if posix.stat(path, "type") == "link" then
    os.remove(path)
    posix.mkdir(path)
  end
end

%if %{shared}
%package        shared
Summary:        Golang shared object libraries

%description    shared
%{summary}.
%endif

%prep
export LANG=C.utf-8
export LC_ALL=C.utf-8
%autosetup -p1 -n go

cp %{SOURCE1} ./src/runtime/

%build
# print out system information
uname -a
cat /proc/cpuinfo
cat /proc/meminfo

# bootstrap compiler GOROOT
%if !%{golang_bootstrap}
export GOROOT_BOOTSTRAP=/
%else
export GOROOT_BOOTSTRAP=%{goroot}
%endif

# set up final install location
export GOROOT_FINAL=%{goroot}

export GOHOSTOS=linux
export GOHOSTARCH=%{gohostarch}

pushd src
# use our gcc options for this build, but store gcc as default for compiler
export CC="%{__cc}"
export CXX="%{__cxx}"
export CC_FOR_TARGET="%{__cc}"
export CFLAGS="%{optflags}"
export LDFLAGS="%{build_ldflags}"
export GOOS=linux
export GOARCH=%{gohostarch}
%if !%{external_linker}
export GO_LDFLAGS="-linkmode internal"
%endif
%if %{cgo_enabled}
export CGO_ENABLED=1
%else
export CGO_ENABLED=0
%endif
./make.bash --no-clean -v
popd

# build shared std lib
%if %{shared}
GOROOT=$(pwd) PATH=$(pwd)/bin:$PATH go install -buildmode=shared -v -x std
%endif

%install
rm -rf %{buildroot}
# remove GC build cache
rm -rf pkg/obj/go-build/*

# create the top level directories
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{goroot}

# install everything into libdir (until symlink problems are fixed)
# https://code.google.com/p/go/issues/detail?id=5830
cp -apv api bin doc lib pkg src misc test VERSION \
   %{buildroot}%{goroot}

# bz1099206
find %{buildroot}%{goroot}/src -exec touch -r %{buildroot}%{goroot}/VERSION "{}" \;
# and level out all the built archives
touch %{buildroot}%{goroot}/pkg
find %{buildroot}%{goroot}/pkg -exec touch -r %{buildroot}%{goroot}/pkg "{}" \;

# remove the doc Makefile
rm -rfv %{buildroot}%{goroot}/doc/Makefile

# put binaries to bindir, linked to the arch we're building,
# leave the arch independent pieces in {goroot}
mkdir -p %{buildroot}%{goroot}/bin/linux_%{gohostarch}
ln -sf %{goroot}/bin/go %{buildroot}%{goroot}/bin/linux_%{gohostarch}/go
ln -sf %{goroot}/bin/gofmt %{buildroot}%{goroot}/bin/linux_%{gohostarch}/gofmt

# ensure these exist and are owned
mkdir -p %{buildroot}%{gopath}/src/github.com
mkdir -p %{buildroot}%{gopath}/src/bitbucket.org
mkdir -p %{buildroot}%{gopath}/src/code.google.com/p
mkdir -p %{buildroot}%{gopath}/src/golang.org/x

# gdbinit
mkdir -p %{buildroot}%{_sysconfdir}/gdbinit.d
cp -av %{SOURCE100} %{buildroot}%{_sysconfdir}/gdbinit.d/golang.gdb

WD="$(pwd)"
cd %{buildroot}
find .%{goroot}/src -name testdata |sed -e 's,^\.,,' >$WD/testfiles.list
find .%{goroot}/src -name "*_test.go" |grep -v '/testdata/' |sed -e 's,^\.,,' >>$WD/testfiles.list
sed -e 's,^,%exclude ,' $WD/testfiles.list >$WD/testfiles-x.list

%check
export GOROOT=$(pwd -P)
export PATH="$GOROOT"/bin:"$PATH"
cd src

export CC="%{__cc}"
export CFLAGS="%{optflags}"
export LDFLAGS="%{build_ldflags}"
%if !%{external_linker}
export GO_LDFLAGS="-linkmode internal"
%endif
%if !%{cgo_enabled} || !%{external_linker}
export CGO_ENABLED=0
%endif

# make sure to not timeout
export GO_TEST_TIMEOUT_SCALE=2

%if %{fail_on_tests}
./run.bash --no-rebuild -v -v -v -k
%else
./run.bash --no-rebuild -v -v -v -k || :
%endif
cd ..

for i in go gofmt; do
	ln -s ../lib/golang/bin/$i %{buildroot}%{_bindir}/
done

# Set some sane defaults
# https://github.com/golang/go/issues/61928
cat >%{buildroot}%{goroot}/go.env <<EOF
GOPROXY=direct
GOSUMDB=off
GOTOOLCHAIN=local
EOF

%files
%doc LICENSE PATENTS
# VERSION has to be present in the GOROOT, for `go install std` to work
%{goroot}/VERSION
%dir %{goroot}
%{goroot}/api
%dir %{goroot}/lib
%{goroot}/lib/time
%config %{goroot}/go.env

# ensure directory ownership, so they are cleaned up if empty
%dir %{gopath}
%dir %{gopath}/src
%dir %{gopath}/src/github.com/
%dir %{gopath}/src/bitbucket.org/
%dir %{gopath}/src/code.google.com/
%dir %{gopath}/src/code.google.com/p/
%dir %{gopath}/src/golang.org
%dir %{gopath}/src/golang.org/x

# gdbinit (for gdb debugging)
%{_sysconfdir}/gdbinit.d/golang.gdb

%files src -f testfiles-x.list
%{goroot}/src
%exclude %{goroot}/src/archive/tar/*_test.go
%exclude %{goroot}/src/archive/tar/testdata
%exclude %{goroot}/src/archive/zip/*_test.go
%exclude %{goroot}/src/archive/zip/testdata

%files docs
%doc %{goroot}/doc

%files misc
%{goroot}/misc

%files tests -f testfiles.list
%{goroot}/test

%files bin
%{_bindir}/go
%{_bindir}/gofmt
%{goroot}/bin
%{goroot}/pkg/linux_*
%{goroot}/pkg/include
%exclude %{goroot}/pkg/linux_*_dynlink
%{goroot}/pkg/tool

%if %{shared}
%files shared
%{goroot}/pkg/linux_*_dynlink
%endif
