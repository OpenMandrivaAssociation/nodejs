# ****ing python 2.x...
%global _python_bytecompile_build 0

Name:           nodejs
Version:        10.15.2
Release:        1
Summary:        JavaScript server-side network application development
Group:          Development/Other
License:        MIT
URL:            http://nodejs.org/
Source0:	https://github.com/nodejs/node/archive/v%{version}.tar.gz
Source100:	%{name}.rpmlintrc

BuildRequires:  libstdc++-devel
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig(libcares)
BuildRequires:	pkgconfig(python2)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	icu-devel >= 60

%description
Evented I/O for Google V8 JavaScript

Node.js use V8 engine (JavaScript engine used for Webkit) and let you create
application on server-side. It handles HTTP server, Socket server, clients
and a lot of modules to ease your projects creation.

Node.js's goal is to provide an easy way to build scalable network programs.

%prep
%setup -q -n node-%{version}
%apply_patches

%build
# Use python 2.x for building...
ln -s `which python2` python
export PATH=`pwd`:$PATH
# Currently, bundled c-ares is newer than the latest released version.
# should use --shared-cares once a newer compatible c-ares is released.
./configure --prefix=%{_prefix} \
%if %mdvver <= 3000000
	--shared-openssl \
%endif
	--with-intl=system-icu \
%if %mdvver >= 3000000
	--shared-cares \
%endif
	--shared-zlib
%make CC=%{__cc} CXX=%{__cxx}

%install
export PATH=`pwd`:$PATH
%makeinstall_std CC=%{__cc} CXX=%{__cxx}

find %{buildroot} -type f -empty -delete

%files
%{_bindir}/node*
%{_bindir}/npm
%{_bindir}/npx
%{_includedir}/node
%{_prefix}/lib/node_modules
%{_mandir}/man1/node.1.*
%{_datadir}/systemtap/tapset/node.stp
%{_docdir}/node/gdbinit
%{_docdir}/node/lldbinit
%{_docdir}/node/lldb_commands.py
