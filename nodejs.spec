Name:           nodejs
Version:        0.8.3
Release:        1
Summary:        JavaScript server-side network application development
Group:          Development/Other
License:        MIT
URL:            http://nodejs.org/
Source0:        http://nodejs.org/dist/v%{version}/node-v%{version}.tar.gz 
BuildRequires:  libstdc++-devel python openssl-devel
BuildRequires:  zlib-devel v8-devel

%description
Evented I/O for Google V8 JavaScript

Node.js use V8 engine (JavaScript engine used for Webkit) and let you create
application on server-side. It handles HTTP server, Socket server, clients
and a lot of modules to ease your projects creation.

Node.js's goal is to provide an easy way to build scalable network programs. 


%prep
%setup -q -n node-v%{version}
#s ed -i "s|/usr/local|%{buildroot}|" tools/installer.js

# http://code.google.com/p/gyp/issues/detail?id=260
sed -i -e "/append('-arch/d" tools/gyp/pylib/gyp/xcode_emulation.py || die


%build

./configure --shared-v8 --prefix=%{buildroot}/%{_prefix} \
	    --shared-v8-includes=%{_includedir} \
	    --openssl-use-sys --shared-zlib
%make

%install
#%makeinstall_std

mkdir -p %{buildroot}/%{_includedir}/node
mkdir -p %{buildroot}/%{_bindir}
mkdir -p %{buildroot}/%{_mandir}
mkdir -p %{buildroot}/lib/node_modules/npm


#/lib/node_modules/npm/man/man1/folders.1


#includes
cp 'src/node.h' 'src/node_buffer.h' 'src/node_object_wrap.h' 'src/node_version.h' %{buildroot}/%{_includedir}/node || die "Failed to copy stuff"
cp 'deps/uv/include/ares.h' 'deps/uv/include/ares_version.h'  %{buildroot}/%{_includedir}/node || die "Failed to copy stuff"
cp 'out/Release/node' %{buildroot}/%{_bindir}/node || die "Failed to copy stuff"


mv -f deps/npm/man/* %{buildroot}/%{_mandir}

cp -R deps/npm/* %{buildroot}/lib/node_modules/npm || die "Failed to copy stuff"
cp -R tools/wafadmin %{buildroot}/lib/node/  || die "Failed to copy stuff"
cp tools/node-waf %{buildroot}/%{_bindir}/ || die "Failed to copy stuff"


ln -s /lib/node_modules/npm/bin/npm-cli.js %{buildroot}/%{_bindir}/npm


#r m -f %{buildroot}/%{_includedir}/node/v8*

%files
%doc doc README.md LICENSE AUTHORS
%{_bindir}/node
%{_bindir}/node-waf
%{_bindir}/npm
%{_includedir}/node*
%{_mandir}/man1/*.xz
%{_mandir}/man3/*.xz
/lib/node_modules/
/lib/node/
