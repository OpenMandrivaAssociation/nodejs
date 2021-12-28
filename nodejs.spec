# As of clang 13.0.0, nodejs 17.3.0,
# -flto and even -flto=thin uses up so much space it'll eventually
# run out of RAM even on a box with 64 GB RAM not doing
# much else...
%define _disable_lto 1
%global optflags %{optflags} -O3

# Broken build system doesn't know about debugsource
%global _empty_manifest_terminate_build 0

# ****ing python 2.x...
#global _python_bytecompile_build 0

Name:		nodejs
Version:	17.3.0
Release:	1
Summary:	JavaScript server-side network application development
Group:		Development/Other
License:	MIT
URL:		http://nodejs.org/
Source0:	https://github.com/nodejs/node/archive/v%{version}.tar.gz
Source100:	%{name}.rpmlintrc
Patch0:		nodejs-link-libatomic.patch
#Patch1:		v8-icu-67.patch
Patch2:		https://src.fedoraproject.org/rpms/nodejs/raw/rawhide/f/0001-Disable-running-gyp-on-shared-deps.patch

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
Requires:	ca-certificates

%description
Evented I/O for Google V8 JavaScript

Node.js use V8 engine (JavaScript engine used for Webkit) and let you create
application on server-side. It handles HTTP server, Socket server, clients
and a lot of modules to ease your projects creation.

Node.js's goal is to provide an easy way to build scalable network programs.

%prep
%autosetup -p1 -n node-%{version}

# remove bundled dependencies that we aren't building
rm -rf deps/zlib
rm -rf deps/brotli

%build
%set_build_flags

# Use python 2.x for building...
#ln -s `which python2` python
#export PATH=`pwd`:$PATH
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
	--openssl-use-def-ca-store

%make_build BUILDTYPE=Release CC="%{__cc}" CXX="%{__cxx}" CFLAGS="%{optflags}" LDFLAGS="%{build_ldflags}"

%install
export PATH=$(pwd):$PATH
%make_install CC=%{__cc} CXX=%{__cxx}

find %{buildroot} -type f -empty -delete

%files
%{_bindir}/node*
%{_bindir}/npm
%{_bindir}/npx
%{_bindir}/corepack
%{_includedir}/node
%{_prefix}/lib/node_modules
%{_mandir}/man1/node.1.*
%{_datadir}/systemtap/tapset/node.stp
%{_docdir}/node/gdbinit
%{_docdir}/node/lldb_commands.py
