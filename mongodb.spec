Name:		mongodb
Version:	1.8.1
Release:	2
Summary:	MongoDB client shell and tools
License:	AGPL 3.0
URL:		http://www.mongodb.org
Group:		Databases

Source0:	http://downloads.mongodb.org/src/%{name}-src-r%{version}.tar.gz
Patch0:		mongodb-1.8.0-spidermonkey-1.8.5-support.patch
Patch1:		mongodb-1.8.1-boost-1.46-support.patch
Patch2:		mongodb-1.8.0-compile-flags.patch
BuildRequires:	mozjs-devel
BuildRequires:	readline-devel
BuildRequires:	boost-devel
BuildRequires:	pcre-devel
BuildRequires:	pcap-devel
BuildRequires:	scons
BuildRequires:	nspr-devel

%description
Mongo (from "huMONGOus") is a schema-free document-oriented database.
It features dynamic profileable queries, full indexing, replication
and fail-over support, efficient storage of large binary data objects,
and auto-sharding.

This package provides the mongo shell, import/export tools, and other
client utilities.

%package	server
Summary:	MongoDB server, sharding server, and support scripts
Group:		Databases
Requires:	mongodb

%description	server
Mongo (from "huMONGOus") is a schema-free document-oriented database.

This package provides the mongo server software, mongo sharding server
softwware, default configuration files, and init.d scripts.

%prep
%setup -qn %{name}-src-r%{version}
%patch0 -p1 -b .mozjs185~
%patch1 -p1 -b .boost_146~
%patch2 -p0 -b .cflags~

%build
%serverbuild
export CXXFLAGS="%optflags -O3 -DBOOST_FILESYSTEM_VERSION=2"
export CPPFLAGS="`pkg-config --cflags mozjs185`"
export LINKFLAGS='%ldflags'
%scons --prefix=%{_prefix}

%install
%serverbuild
export CXXFLAGS="%optflags -O3 -DBOOST_FILESYSTEM_VERSION=2"
export CPPFLAGS="`pkg-config --cflags mozjs185`"
export LINKFLAGS='%ldflags'


%scons --prefix=$RPM_BUILD_ROOT%{_usr} install
mkdir -p $RPM_BUILD_ROOT%{_mandir}/man1
cp debian/*.1 $RPM_BUILD_ROOT%{_mandir}/man1/
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d
cp rpm/init.d-mongod $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/mongod
chmod a+x $RPM_BUILD_ROOT%{_sysconfdir}/rc.d/init.d/mongod
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}
cp rpm/mongod.conf $RPM_BUILD_ROOT%{_sysconfdir}/mongod.conf
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
cp rpm/mongod.sysconfig $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/mongod
mkdir -p $RPM_BUILD_ROOT%{_var}/lib/mongo
mkdir -p $RPM_BUILD_ROOT%{_var}/log/mongo
touch $RPM_BUILD_ROOT%{_var}/log/mongo/mongod.log

%pre server
%_pre_useradd mongod /var/lib/mongo /bin/false

%post server
%_post_service mongod

%preun server
%_preun_service mongod

%postun server
%_postun_userdel mongod

%files
%doc README GNU-AGPL-3.0.txt

%{_bindir}/mongo
%{_bindir}/mongodump
%{_bindir}/mongoexport
%{_bindir}/mongofiles
%{_bindir}/mongoimport
%{_bindir}/mongorestore
%{_bindir}/mongostat
%{_bindir}/mongosniff
%{_bindir}/bsondump
%{_mandir}/man1/mongo.1*
%{_mandir}/man1/mongodump.1*
%{_mandir}/man1/mongoexport.1*
%{_mandir}/man1/mongofiles.1*
%{_mandir}/man1/mongoimport.1*
%{_mandir}/man1/mongosniff.1*
%{_mandir}/man1/mongostat.1*
%{_mandir}/man1/mongorestore.1*

%files server
%config(noreplace) %{_sysconfdir}/mongod.conf
%{_bindir}/mongod
%{_bindir}/mongos
%{_mandir}/man1/mongod.1*
%{_mandir}/man1/mongos.1*
%{_sysconfdir}/rc.d/init.d/mongod
%{_sysconfdir}/sysconfig/mongod
%attr(0755,mongod,mongod) %dir %{_var}/lib/mongo
%attr(0755,mongod,mongod) %dir %{_var}/log/mongo
%attr(0640,mongod,mongod) %config(noreplace) %verify(not md5 size mtime) %{_var}/log/mongo/mongod.log
