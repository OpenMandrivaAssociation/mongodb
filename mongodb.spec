%define debug_package %nil

Name:    mongodb
Version: 3.2.10
Release: 1
Summary: MongoDB client shell and tools
License: AGPL 3.0
URL: http://www.mongodb.org
Group: Databases
Source0: http://downloads.mongodb.org/src/%{name}-src-r%{version}.tar.gz
Source1: mongod.service
Patch0:  mongodb-3.2.4-boost-1.60.patch
Patch1:	 system-libs.patch
BuildRequires: readline-devel
BuildRequires: boost-devel
BuildRequires: pcre-devel
BuildRequires: libstemmer-devel
BuildRequires: snappy-devel
BuildRequires: pkgconfig(openssl)
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
%apply_patches
# disable propagation of $TERM env var into the Scons build system
sed -i -r "s|(for key in \('HOME'), 'TERM'(\):)|\1\2|" SConstruct
sed -i -e "s/\[\"yaml\"\]/\[\"yaml-cpp\"\]/" SConstruct
# Use system versions of header files (bundled does not differ)
sed -i -r "s|third_party/libstemmer_c/include/libstemmer.h|libstemmer/libstemmer.h|" src/mongo/db/fts/stemmer.h
sed -i -r "s|third_party/yaml-cpp-0.5.1/include/yaml-cpp/yaml.h|yaml-cpp/yaml.h|" src/mongo/util/options_parser/options_parser.cpp

%build
%serverbuild
export CXXFLAGS="%optflags"
export LINKFLAGS='%ldflags'
export CC=%{__cc}
export CXX=%{__cxx}
%scons --prefix=%{_prefix} \
	CC=%{__cc} CXX=%{__cxx} \
	--use-system-pcre \
	--use-system-boost \
	--use-system-zlib \
	--ssl \
	--use-system-yaml \
	--use-system-snappy \
	--disable-warnings-as-errors 

%install
%serverbuild
export CXXFLAGS="%optflags"
export LINKFLAGS='%ldflags'
export CC=%{__cc}
export CXX=%{__cxx}

%scons --prefix=%{buildroot}%{_usr} \
	--use-system-pcre \
	CC=%{__cc} CXX=%{__cxx} \
	--use-system-boost \
	--use-system-zlib \
	--use-system-yaml \
	--use-system-snappy \
	--disable-warnings-as-errors install

mkdir -p %{buildroot}%{_mandir}/man1
cp debian/*.1 %{buildroot}%{_mandir}/man1/
mkdir -p %{buildroot}%{_unitdir}
cp %{SOURCE1} %{buildroot}%{_unitdir}/mongod.service
mkdir -p %{buildroot}%{_sysconfdir}
cp rpm/mongod.conf %{buildroot}%{_sysconfdir}/mongod.conf
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cp rpm/mongod.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/mongod
mkdir -p %{buildroot}%{_var}/lib/mongo
mkdir -p %{buildroot}%{_var}/log/mongodb
touch %{buildroot}%{_var}/log/mongodb/mongod.log

cat >> %{buildroot}%{_sysconfdir}/sysconfig/mongod << EOF
OPTIONS="-f /etc/mongod.conf"
EOF

# (cg) Ensure the pid file folder exists (this is more important under mga3
# when /var/run will be on tmpfs)
mkdir -p %{buildroot}%{_tmpfilesdir}
cat > %{buildroot}%{_tmpfilesdir}/%{name}-server.conf << EOF
d %{_var}/run/mongo 0755 mongod mongod -
EOF

rm -f %{buildroot}/usr/lib/libmongoclient.a

%pre server
%_pre_useradd mongod /var/lib/mongo /bin/false

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
%{_tmpfilesdir}/%{name}-server.conf
%{_unitdir}/mongod.service
%{_sysconfdir}/sysconfig/mongod
%attr(0755,mongod,mongod) %dir %{_var}/lib/mongo
%attr(0755,mongod,mongod) %dir %{_var}/log/mongodb
%attr(0640,mongod,mongod) %verify(not md5 size mtime) %{_var}/log/mongodb/mongod.log

