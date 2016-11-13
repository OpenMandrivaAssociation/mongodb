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
BuildRequires: pkgconfig(mozjs185)
BuildRequires: pkgconfig(libtcmalloc)
BuildRequires: pcap-devel
BuildRequires: scons
BuildRequires: valgrind-devel

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
	--js-engine=mozjs \
	--server-js=on \
	--use-system-valgrind \
	--use-system-tcmalloc \
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
	--ssl \
	--use-system-yaml \
	--use-system-snappy \
	--js-engine=mozjs \
	--server-js=on \
	--use-system-valgrind \
	--use-system-tcmalloc \
	--disable-warnings-as-errors install

mkdir -p %{buildroot}%{_mandir}/man1/
cp debian/*.1 %{buildroot}%{_mandir}/man1/
install -m644 %{SOURCE1} -D %{buildroot}%{_unitdir}/mongod.service
install -m644 rpm/mongod.conf -D %{buildroot}%{_sysconfdir}/mongod.conf
install -m644 rpm/mongod.sysconfig -D %{buildroot}%{_sysconfdir}/sysconfig/mongod
mkdir -p %{buildroot}%{_sharedstatedir}/mongo
mkdir -p %{buildroot}%{_logdir}/mongodb

cat >> %{buildroot}%{_sysconfdir}/sysconfig/mongod << EOF
OPTIONS="-f /etc/mongod.conf"
EOF

# (cg) Ensure the pid file folder exists (this is more important under mga3
# when /var/run will be on tmpfs)
mkdir -p %{buildroot}%{_tmpfilesdir}
cat > %{buildroot}%{_tmpfilesdir}/%{name}-server.conf << EOF
d %{_varrundir}/mongo 0755 mongod mongod -
EOF

%pre server
%_pre_useradd mongod /var/lib/mongo /bin/nologin

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
%config(noreplace) %{_sysconfdir}/sysconfig/mongod
%attr(0755,mongod,mongod) %dir %{_sharedstatedir}/mongo
%attr(0750,mongod,mongod) %dir %{_logdir}/mongodb
%attr(0640,mongod,mongod) %ghost %{_logdir}/mongodb/mongod.log

