Name:           nodejs
Version:        0.8.2
Release:        1
Summary:        JavaScript server-side network application development
Group:          Development/Other
License:        MIT
URL:            http://nodejs.org/
Source0:        http://nodejs.org/dist/node-v%{version}.tar.gz 

BuildRequires:  libstdc++-devel
BuildRequires:	openssl-devel
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
./configure --prefix=%{_prefix}
%make

%install
%makeinstall_std

%files
%defattr(-,root,root,-)
%doc doc README.md LICENSE AUTHORS ChangeLog
%attr(755,root,root) %{_bindir}/node
%attr(755,root,root) %{_bindir}/node-waf
%{_bindir}/npm
%{_mandir}/man1/node.1*
%{_includedir}/node*
%{_prefix}/lib/node*

%changelog
* Wed May 18 2011 Eugeni Dodonov <eugeni@mandriva.com> 0.4.7-1
+ Revision: 676071
- Fix group
- Imported node.js
- Created package structure for nodejs.

