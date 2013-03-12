Name:           nodejs
Version:        0.9.9
Release:        1
Summary:        JavaScript server-side network application development
Group:          Development/Other
License:        MIT
URL:            http://nodejs.org/
Source0:        http://nodejs.org/dist/v%{version}/node-v%{version}.tar.gz 

BuildRequires:  libstdc++-devel
BuildRequires:	openssl-devel
BuildRequires:	v8-devel
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
./configure --prefix=%{_prefix} \
	--openssl-use-sys \
	--shared-zlib \
	--shared-v8 \
	--shared-cares
%make

%install
%makeinstall_std

%files
%{_bindir}/node*
%{_bindir}/npm
%{_prefix}/lib/node_modules
%{_prefix}/lib/dtrace/node.d
%{_mandir}/man1/node.1.*
