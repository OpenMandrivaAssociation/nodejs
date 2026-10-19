# As of clang 13.0.0, nodejs 17.3.0,
# -flto and even -flto=thin uses up so much space it'll eventually
# run out of RAM even on a box with 64 GB RAM not doing
# much else...
%global _disable_lto 1
# V8 + clang on every core OOMs the builder (and the host). Cap jobs
# and do not emit -g3 debug info during the compile.
%global _smp_ncpus_max 4
%global optflags %{optflags} -O3 -g1

# SONAME major of the V8 in this Node release. The build compares it
# with v8-version.h so a newer Node cannot silently ship another major.
%global v8_major 14
%global libname %mklibname v8
%global devname %mklibname -d v8
%global oldlibname %mklibname v8 7

# Broken build system doesn't know about debugsource
%undefine _debugsource_packages

Name:		nodejs
Version:	26.12.0
Release:	2
Summary:	JavaScript server-side network application development
Group:		Development/Other
License:	MIT
URL:		https://nodejs.org/
Source0:	https://github.com/nodejs/node/archive/v%{version}.tar.gz
Source100:	%{name}.rpmlintrc

BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	slibtool
BuildRequires:	libstdc++-devel
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(libcares)
BuildRequires:	pkgconfig(libuv)
BuildRequires:	pkgconfig(libnghttp2)
BuildRequires:	pkgconfig(libbrotlidec)
BuildRequires:	pkgconfig(libbrotlienc)
BuildRequires:	pkgconfig(python3)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	icu-devel >= 60
BuildRequires:	atomic-devel
BuildRequires:	ninja
BuildRequires:	make
Requires:	ca-certificates
# Just so we get Provides: nodejs(engine) and friends
BuildRequires:	nodejs-packaging
# npm is a separate package on some other distros, let's
# try to keep depending packages compatible
Provides:	npm = %{EVRD}
Provides:	nodejs(engine) = %{EVRD}

%description
Evented I/O for Google V8 JavaScript

Node.js use V8 engine (JavaScript engine used for Webkit) and let you create
application on server-side. It handles HTTP server, Socket server, clients
and a lot of modules to ease your projects creation.

Node.js's goal is to provide an easy way to build scalable network programs.

%package -n %{libname}
Summary:	V8 JavaScript engine built from Node.js
Group:		System/Libraries
License:	BSD-3-Clause and Apache-2.0 and MIT and zlib
%rename		%{oldlibname}
%rename		v8

%description -n %{libname}
Shared V8 built from the Node.js %{version} sources. Pointer compression and
the sandbox stay off, the same way the node binary is built. This is the V8
embedders should link. It is not a newer V8 than the one inside Node.
The library also contains the Abseil, Highway, simdutf and Temporal code
Node links into V8. This replaces the standalone V8 7.4 packages.

%package -n %{devname}
Summary:	Development files for V8
Group:		Development/C
License:	BSD-3-Clause and Apache-2.0 and MIT and zlib
Requires:	%{libname} = %{EVRD}
Requires:	nodejs = %{EVRD}
Provides:	v8-devel = %{EVRD}

%description -n %{devname}
Headers and link flags for libv8.so.%{v8_major}. The unversioned libv8.so
symlink points at that library. Public headers are the copies Node installs
under %{_includedir}/node, and %{_includedir}/v8.h is the current V8.

%prep
%autosetup -p1 -n node-%{version}

# remove bundled dependencies that we aren't building
#rm -rf deps/zlib
rm -rf deps/brotli

%build
%set_build_flags
# lld defaults to one thread per core; one V8 link is already huge
export LDFLAGS="${LDFLAGS} -Wl,--threads=1"
# The static V8 archives are relinked into libv8.so below.
# local-exec TLS cannot go into a shared library. This switches V8 to
# the local-dynamic model it uses for component builds.
export CFLAGS="${CFLAGS} -fPIC"
export CXXFLAGS="${CXXFLAGS} -fPIC -DV8_TLS_USED_IN_LIBRARY"

# Currently, bundled c-ares is newer than the latest released version.
# should use --shared-cares once a newer compatible c-ares is released.
# Might want to add --shared-http-parser at some point
./configure --prefix=%{_prefix} \
	--shared-openssl \
	--shared-brotli \
	--shared-libuv \
	--shared-nghttp2 \
	--with-intl=system-icu \
	--shared-cares \
	--shared-zlib \
	--openssl-use-def-ca-store \
	--ninja

# cctest/embedtest are extra multi-GB links.
%ninja_build -C out/Release node

# Node links V8 into the node binary and does not install a library.
# Rebuild those same archives as libv8.so.<major>. The archive list is
# whatever this build actually linked, in that order.
python - << 'PY'
from pathlib import Path
lines = Path("out/Release/obj/node.ninja").read_text().splitlines()
joined = []
buf = ""
for line in lines:
    if line.endswith("$"):
        buf += line[:-1] + " "
    else:
        joined.append(buf + line)
        buf = ""
if buf:
    joined.append(buf)
link = next((ln for ln in joined if ln.startswith("build node: link ")), None)
if link is None:
    raise SystemExit("node link line not found")
arch = []
seen = set()
for part in link.split(" link ", 1)[1].split():
    if part in ("|", "||"):
        break
    if part.endswith(".a") and "/v8_gypfiles/lib" in part and part not in seen:
        seen.add(part)
        arch.append(part)
if not arch:
    raise SystemExit("no V8 archives on the node link line")
Path("out/Release/v8-archives.txt").write_text("\n".join(arch) + "\n")
print("V8 archives:")
print("\n".join(arch))
PY

V8_MAJOR=$(sed -n 's/^#define V8_MAJOR_VERSION[[:space:]]*//p' deps/v8/include/v8-version.h)
V8_MINOR=$(sed -n 's/^#define V8_MINOR_VERSION[[:space:]]*//p' deps/v8/include/v8-version.h)
V8_BUILD=$(sed -n 's/^#define V8_BUILD_NUMBER[[:space:]]*//p' deps/v8/include/v8-version.h)
V8_PATCH=$(sed -n 's/^#define V8_PATCH_LEVEL[[:space:]]*//p' deps/v8/include/v8-version.h)
V8_VER="${V8_MAJOR}.${V8_MINOR}.${V8_BUILD}.${V8_PATCH}"
echo "${V8_VER}" > out/Release/v8.ver
echo "${V8_MAJOR}" > out/Release/v8.major
echo "V8 ${V8_VER}"
if [ "${V8_MAJOR}" != "%{v8_major}" ]; then
	echo "V8 SONAME major ${V8_MAJOR} does not match the packaged major %{v8_major}" >&2
	exit 1
fi
PREFIX=%{_prefix} LIBDIR_REL=%{_lib} python - << 'PY'
import os
from pathlib import Path
ver = Path("out/Release/v8.ver").read_text().strip()
major = Path("out/Release/v8.major").read_text().strip()
dollar = "$"
pc = (
    "prefix=" + os.environ["PREFIX"] + "\n"
    "libdir=" + dollar + "{prefix}/" + os.environ["LIBDIR_REL"] + "\n"
    "includedir=" + dollar + "{prefix}/include\n"
    "Name: v8\n"
    "Description: V8 JavaScript engine built from Node.js\n"
    "Version: " + ver + "\n"
    "Libs: -L" + dollar + "{libdir} -lv8\n"
    "Cflags: -I" + dollar + "{includedir} -DUSING_V8_SHARED -DUSING_V8_PLATFORM_SHARED\n"
)
Path("out/Release/v8.pc").write_text(pc)
print(pc)
PY

# Archive paths in v8-archives.txt are relative to out/Release.
# shellcheck disable=SC2046
(
	cd out/Release
	# gen/release/libnode_crates.a holds the Rust temporal_capi that V8's
	# Temporal builtins call. It is not a v8_gypfiles archive.
	c++ -shared ${LDFLAGS} \
		-Wl,-soname,libv8.so.${V8_MAJOR} \
		-Wl,--whole-archive $(cat v8-archives.txt) -Wl,--no-whole-archive \
		gen/release/libnode_crates.a \
		$(pkg-config --libs icu-uc icu-i18n) -latomic -lz -ldl -pthread \
		-o libv8.so.${V8_MAJOR}
)

# V8 14 headers reject anything older than C++20.
cat > v8smoke.cc << 'EOF'
#include "v8.h"
#include "libplatform/libplatform.h"
#include <cstring>
int main() {
	v8::V8::SetFlagsFromString("--jitless");
	if (!v8::platform::NewDefaultPlatform())
		return 1;
	const char *v = v8::V8::GetVersion();
	return (v && std::strncmp(v, "14.", 3) == 0) ? 0 : 2;
}
EOF
ln -s libv8.so.${V8_MAJOR} out/Release/libv8.so
c++ -std=c++20 -DUSING_V8_SHARED -DUSING_V8_PLATFORM_SHARED \
	-I deps/v8/include v8smoke.cc \
	-L out/Release -lv8 \
	$(pkg-config --libs icu-uc icu-i18n) -latomic -lz -ldl -pthread \
	-o v8smoke
LD_LIBRARY_PATH=out/Release ./v8smoke
nm -D out/Release/libv8.so.${V8_MAJOR} | grep -q 'SetFlagsFromString'

%install
export PATH=$(pwd):$PATH
%make_install CC=%{__cc} CXX=%{__cxx}

find %{buildroot} -type f -empty -delete

ln -s node %{buildroot}%{_bindir}/nodejs

V8_MAJOR=$(cat out/Release/v8.major)
install -D -m755 out/Release/libv8.so.${V8_MAJOR} %{buildroot}%{_libdir}/libv8.so.${V8_MAJOR}
ln -s libv8.so.${V8_MAJOR} %{buildroot}%{_libdir}/libv8.so
install -D -m644 out/Release/v8.pc %{buildroot}%{_libdir}/pkgconfig/v8.pc
# Node's install.py omits include/v8-inspector.h. The inspector is already
# linked into libv8.so, and OnlyOffice includes this header.
install -m644 deps/v8/include/v8-inspector.h %{buildroot}%{_includedir}/node/v8-inspector.h
# Quoted includes are resolved next to v8.h, not next to the Node copy.
for h in %{buildroot}%{_includedir}/node/v8*.h; do
	base=${h##*/}
	ln -s "node/${base}" "%{buildroot}%{_includedir}/${base}"
done
ln -s node/cppgc %{buildroot}%{_includedir}/cppgc
ln -s node/libplatform %{buildroot}%{_includedir}/libplatform

%files
%{_bindir}/node*
%{_bindir}/npm
%{_bindir}/npx
%{_includedir}/node
%{_prefix}/lib/node_modules
%{_mandir}/man1/node.1.*
%{_docdir}/node/gdbinit
%{_docdir}/node/lldb_commands.py

%files -n %{libname}
%{_libdir}/libv8.so.*

%files -n %{devname}
%{_libdir}/libv8.so
%{_libdir}/pkgconfig/v8.pc
%{_includedir}/v8*.h
%{_includedir}/cppgc
%{_includedir}/libplatform
