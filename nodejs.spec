Name:           nodejs
Version:        0.11.14
Release:        1
Summary:        JavaScript server-side network application development
Group:          Development/Other
License:        MIT
URL:            http://nodejs.org/
Source0:        http://nodejs.org/dist/v%{version}/node-v%{version}.tar.gz 
Source100:	%{name}.rpmlintrc

BuildRequires:  libstdc++-devel
BuildRequires:	openssl-devel
BuildRequires:	pkgconfig(libcares)
BuildRequires:	pkgconfig(python)

%description
Evented I/O for Google V8 JavaScript

Node.js use V8 engine (JavaScript engine used for Webkit) and let you create
application on server-side. It handles HTTP server, Socket server, clients
and a lot of modules to ease your projects creation.

Node.js's goal is to provide an easy way to build scalable network programs. 

%prep
%setup -q -n node-v%{version}

%build
# Use python 2.x for building...
ln -s `which python2` python
export PATH=`pwd`:$PATH
# Currently, bundled c-ares is newer than the latest released version.
# should use --shared-cares once a newer compatible c-ares is released.
./configure --prefix=%{_prefix} \
	--openssl-use-sys \
	--shared-zlib
%make

%install
export PATH=`pwd`:$PATH
%makeinstall_std

%files
%{_bindir}/node*
%{_bindir}/npm
%{_includedir}/node
%{_prefix}/lib/node_modules
%{_mandir}/man1/node.1.*
%{_datadir}/systemtap/tapset/node.stp
