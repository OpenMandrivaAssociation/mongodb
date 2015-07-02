%define debug_package %nil

Name:    mongodb
Version: 3.0.4
Release: 1
Summary: MongoDB client shell and tools
License: AGPL 3.0
URL: http://www.mongodb.org
Group: Databases
Source0: http://downloads.mongodb.org/src/%{name}-src-r%{version}.tar.gz
Source1: mongod.service
BuildRequires: readline-devel
BuildRequires: boost-devel
BuildRequires: pcre-devel
BuildRequires: pkgconfig(libpcre)
BuildRequires: pkgconfig(yaml-cpp)
BuildRequires: pcap-devel
BuildRequires: scons

%description
Mongo (from "huMONGOus") is a schema-free document-oriented database.
It features dynamic profileable queries, full indexing, replication
and fail-over support, efficient storage of large binary data objects,
and auto-sharding.

This package provides the mongo shell, import/export tools, and other
client utilities.

%package server
Summary: MongoDB server, sharding server, and support scripts
Group: Databases
Requires: mongodb
Requires(post):  rpm-helper >= 0.24.1-1
Requires(preun): rpm-helper >= 0.24.1-1


%description server
Mongo (from "huMONGOus") is a schema-free document-oriented database.

This package provides the mongo server software, mongo sharding server
softwware, default configuration files, and init.d scripts.


%prep
%setup -qn %{name}-src-r%{version}
sed -i -e "s/\[\"yaml\"\]/\[\"yaml-cpp\"\]/" SConstruct

%build
%serverbuild
export CXXFLAGS="%optflags"
export LINKFLAGS='%ldflags'
%scons --prefix=%{_prefix} --use-system-pcre --use-system-boost --use-system-zlib --use-system-yaml

%install
%serverbuild
export CXXFLAGS="%optflags"
export LINKFLAGS='%ldflags'

%scons --prefix=%{buildroot}%{_usr} --use-system-pcre --use-system-boost --use-system-zlib --use-system-yaml install
mkdir -p %{buildroot}%{_mandir}/man1
cp debian/*.1 %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_unitdir}
cp %{SOURCE1} %{buildroot}%{_unitdir}/mongod.service
mkdir -p %{buildroot}%{_sysconfdir}/rc.d/init.d
cp rpm/init.d-mongod %{buildroot}%{_sysconfdir}/rc.d/init.d/mongod
chmod a+x %{buildroot}%{_sysconfdir}/rc.d/init.d/mongod
mkdir -p %{buildroot}%{_sysconfdir}
cp rpm/mongod.conf %{buildroot}%{_sysconfdir}/mongod.conf
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cp rpm/mongod.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/mongod
mkdir -p %{buildroot}%{_var}/lib/mongo
mkdir -p %{buildroot}%{_var}/log/mongo
touch %{buildroot}%{_var}/log/mongo/mongod.log

cat >> %{buildroot}%{_sysconfdir}/sysconfig/mongod << EOF
OPTIONS="-f /etc/mongod.conf"
EOF

# (cg) Ensure the pid file folder exists (this is more important under mga3
# when /var/run will be on tmpfs)
mkdir -p %{buildroot}%{_prefix}/lib/tmpfiles.d
cat > %{buildroot}%{_prefix}/lib/tmpfiles.d/%{name}-server.conf << EOF
d %{_var}/run/mongo 0755 mongod mongod -
EOF

rm -f %{buildroot}/usr/lib/libmongoclient.a

%pre server
%_pre_useradd mongod /var/lib/mongo /bin/false

%post server
# (cg) Make sure the pid folder exists on install
mkdir -p %{_var}/run/mongo
chown mongod.mongod %{_var}/run/mongo
%_post_service mongod

%preun server
%_preun_service mongod

%postun server
%_postun_userdel mongod

%files
%doc README GNU-AGPL-3.0.txt
%{_bindir}/mongo
%{_bindir}/mongoperf
%{_bindir}/mongosniff
%{_mandir}/man1/mongo.1*
%{_mandir}/man1/mongodump.1*
%{_mandir}/man1/mongoexport.1*
%{_mandir}/man1/mongofiles.1*
%{_mandir}/man1/mongoimport.1*
%{_mandir}/man1/mongosniff.1*
%{_mandir}/man1/mongostat.1*
%{_mandir}/man1/mongorestore.1*
%{_mandir}/man1/bsondump.1*
%{_mandir}/man1/mongooplog.1.*
%{_mandir}/man1/mongoperf.1.*
%{_mandir}/man1/mongotop.1.*

%files server
%config(noreplace) %{_sysconfdir}/mongod.conf
%{_bindir}/mongod
%{_bindir}/mongos
%{_mandir}/man1/mongod.1*
%{_mandir}/man1/mongos.1*
%{_prefix}/lib/tmpfiles.d/%{name}-server.conf
%{_unitdir}/mongod.service
%{_sysconfdir}/rc.d/init.d/mongod
%{_sysconfdir}/sysconfig/mongod
%attr(0755,mongod,mongod) %dir %{_var}/lib/mongo
%attr(0755,mongod,mongod) %dir %{_var}/log/mongo
%attr(0640,mongod,mongod) %config(noreplace) %verify(not md5 size mtime) %{_var}/log/mongo/mongod.log

