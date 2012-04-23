Name:           nodejs
Version:        0.6.15
Release:        1
Summary:        JavaScript server-side network application development
Group:          Development/Other
License:        MIT
URL:            http://nodejs.org/
Source0:        http://nodejs.org/dist/v%{version}/node-v%{version}.tar.gz 
BuildRequires:  libstdc++-devel python openssl-devel
BuildRequires:  zlib-devel

%description
Evented I/O for Google V8 JavaScript

Node.js use V8 engine (JavaScript engine used for Webkit) and let you create
application on server-side. It handles HTTP server, Socket server, clients
and a lot of modules to ease your projects creation.

Node.js's goal is to provide an easy way to build scalable network programs. 


%prep
%setup -q -n node-v%{version}

%build
./configure --prefix=%{_prefix}
%make

%install
%makeinstall_std

%files
%doc doc README.md LICENSE AUTHORS
%attr(755,root,root) %{_bindir}/node
%attr(755,root,root) %{_bindir}/npm
#%attr(755,root,root) %{_bindir}/node_g
%attr(755,root,root) %{_bindir}/node-waf
%{_mandir}/man1/node.1*
%{_includedir}/node*
#%{_prefix}/lib/pkgconfig/nodejs.pc
%{_prefix}/lib/node*

