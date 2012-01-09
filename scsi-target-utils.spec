Name:           scsi-target-utils
Version:        1.0.4
Release:        3%{?dist}
Summary:        The SCSI target daemon and utility programs

Group:          System Environment/Daemons
License:        GPLv2
URL:            http://stgt.sourceforge.net/
Source0:        http://stgt.sourceforge.net/releases/tgt-1.0.4.tar.gz
Source1:        tgtd.init
Source2:        sysconfig.tgtd
Source3:        targets.conf
# Add Red Hat specific info to docs.
Patch0:         scsi-target-utils-redhatify-docs.patch
# Allow user to use tgtd with or without iser without having to recompile.
Patch1:         scsi-target-utils-dynamic-link-iser.patch
# Workaround for missing __NR_eventfd on archs that do not support it.
Patch2:         scsi-target-utils-hack-check-for-eventfd.patch
# Add iSNS targets.conf support from upstream
Patch3:         scsi-target-utils-isns-targets-conf.patch
# Fix Fix tgt-admin logic error with shared accounts in targets.conf 
Patch4:         scsi-target-utils-fix-shared-accts.patch
# Fix iSNS overflow bugs
Patch5:         scsi-target-utils-fix-isns-of.patch
# Fix iSNS mem bugs
Patch6:         scsi-target-utils-fix-isns-mem.patch

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  pkgconfig libibverbs-devel librdmacm-devel
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
ExcludeArch:    s390 s390x

%description
The SCSI target package contains the daemon and tools to setup a SCSI targets.
Currently, software iSCSI targets are supported.


%prep
%setup -q -n tgt-1.0.4
%patch0 -p1 -b .redhatify-docs
%patch1 -p1 -b .dynamic-link-iser
%patch2 -p1 -b .hack-check-for-eventfd
%patch3 -p1 -b .isns-targets-conf
%patch4 -p1 -b .fix-shared-accts
%patch5 -p1 -b .fix-isns-of
%patch6 -p1 -b .fix-isns-mem

%build
pushd usr
%{__sed} -i -e 's|-Wall -g -O2|%{optflags}|' Makefile
%{__make} %{?_smp_mflags} ISCSI=1 ISCSI_RDMA=1
popd


%install
%{__rm} -rf %{buildroot}
%{__install} -d %{buildroot}%{_sbindir}
%{__install} -d %{buildroot}%{_mandir}/man8
%{__install} -d %{buildroot}%{_initrddir}
%{__install} -d %{buildroot}/etc/tgt
%{__install} -d %{buildroot}/etc/sysconfig

%{__install} -p -m 0755 scripts/tgt-setup-lun %{buildroot}%{_sbindir}
%{__install} -p -m 0755 %{SOURCE1} %{buildroot}%{_initrddir}/tgtd
%{__install} -p -m 0755 scripts/tgt-admin %{buildroot}/%{_sbindir}/tgt-admin
%{__install} -p -m 0644 doc/manpages/tgtadm.8 %{buildroot}/%{_mandir}/man8
%{__install} -p -m 0644 doc/manpages/tgt-admin.8 %{buildroot}/%{_mandir}/man8
%{__install} -p -m 0644 doc/manpages/tgt-setup-lun.8 %{buildroot}/%{_mandir}/man8
%{__install} -p -m 0600 %{SOURCE2} %{buildroot}/etc/sysconfig/tgtd
%{__install} -p -m 0600 %{SOURCE3} %{buildroot}/etc/tgt

pushd usr
%{__make} install DESTDIR=%{buildroot} sbindir=%{_sbindir}


%post
/sbin/chkconfig --add tgtd

%postun
if [ "$1" = "1" ] ; then
     /sbin/service tgtd condrestart > /dev/null 2>&1 || :
fi

%preun
if [ "$1" = "0" ] ; then
     /sbin/chkconfig tgtd stop > /dev/null 2>&1
     /sbin/chkconfig --del tgtd
fi


%clean
%{__rm} -rf %{buildroot}


%files
%defattr(-, root, root, -)
%doc README doc/README.iscsi doc/README.iser doc/README.lu_configuration doc/README.mmc
%{_sbindir}/tgtd
%{_sbindir}/tgtadm
%{_sbindir}/tgt-setup-lun
%{_sbindir}/tgt-admin
%{_sbindir}/tgtimg
%{_mandir}/man8/*
%{_initrddir}/tgtd
%attr(0600,root,root) %config(noreplace) /etc/sysconfig/tgtd
%attr(0600,root,root) %config(noreplace) /etc/tgt/targets.conf


%changelog
* Thu Jul 8 2010 Mike Christie <mchristie@redhat.com> - 1.0.4-3
- 584426 Make init scripts LSB-compilant

* Tue Jun 29 2010 Mike Christie <mchristie@redhat.com> - 1.0.4-2
- Fix iSNS scn pdu overflows (CVE-2010-2221).

* Fri May 7 2010 Mike Christie <mchristie@redhat.com> - 1.0.4-1
- 589803 Fix iser rpm dependencies

* Wed May 5 2010 Mike Christie <mchristie@redhat.com> - 1.0.4-0
- 587072 Fix tgt-admin logic error with shared accounts in targets.conf 
- Rebase to 1.0.4 to sync fixes.

* Thu Apr 8 2010 Mike Christie <mchristie@redhat.com> - 1.0.1-3
- 576359 Fix format string vulnerability  (CVE-2010-0743)

* Wed Mar 31 2010 Mike Christie <mchristie@redhat.com> - 1.0.1-2
- 578274 - Support iSNS settings in targets.conf

* Mon Feb 8 2010 Mike Christie <mchristie@redhat.com> - 1.0.1-1
- Add spec patch comments.

* Thu Feb 4 2010 Mike Christie <mchristie@redhat.com> - 1.0.1-0
- Rebase to 1.0.1 release, and update spec http references to reflect
project moved to sourceforge.

* Wed Jan 13 2010 Mike Christie <mchristie@redhat.com> - 0.9.11-1.20091205snap
- 549683 Rebuild for RHEL-6

* Mon Dec 21 2009 Hans de Goede <hdegoede@redhat.com> - 0.9.11-1.20091205snap
- Rebase to 0.9.11 + some fixes from git (git id
  97832d8dcd00202a493290b5d134b581ce20885c)
- Rewrite initscript, make it follow:
  http://fedoraproject.org/wiki/Packaging/SysVInitScript
  And merge in RHEL-5 initscript improvements:
  - Parse /etc/tgt/targets.conf, which allows easy configuration of targets
  - Better initiator status checking in stop
  - Add force-stop, to stop even when initiators are still connected
  - Make reload reload configuration from /etc/tgt/targets.conf without
    stopping tgtd (but only for unused targets)
  - Add force-reload (reloads configs for all targets including busy ones)

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 0.9.5-3
- rebuilt with new openssl

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Mon Mar 16 2009 Terje Rosten <terje.rosten@ntnu.no> - 0.9.5-1
- 0.9.5
- remove patch now upstream
- add patch to fix mising destdir in usr/Makefile
- mktape and dump_tape has moved to tgtimg
- add more docs

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9.2-3
- rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sat Jan 17 2009 Tomas Mraz <tmraz@redhat.com> - 0.9.2-2
- rebuild with new openssl

* Tue Dec 16 2008 Jarod Wilson <jarod@redhat.com> - 0.9.2-1
- update to 0.9.2 release

* Tue Oct 21 2008 Terje Rosten <terje.rosten@ntnu.no> - 0.0-6.20080805snap
- add tgt-admin man page, tgt-admin and tgt-core-test

* Fri Aug 22 2008 Terje Rosten <terje.rosten@ntnu.no> - 0.0-5.20080805snap
- update to 20080805 snapshot

* Sun Feb 10 2008 Terje Rosten <terje.rosten@ntnu.no> - 0.0-4.20071227snap
- update to 20071227 snapshot
- add patch to compile with newer glibc

* Sat Feb  9 2008 Terje Rosten <terje.rosten@ntnu.no> - 0.0-3.20070803snap
- rebuild

* Sun Dec 07 2007 Alex Lancaster <alexlan[AT]fedoraproject.org> - 0.0-2.20070803snap
- rebuild for new openssl soname bump

* Wed Sep 26 2007 Terje Rosten <terje.rosten@ntnu.no> - 0.0-1.20070803snap
- random cleanup

* Wed Sep 26 2007 Terje Rosten <terje.rosten@ntnu.no> - 0.0-0.20070803snap
- update to 20070803
- fix license tag
- use date macro
- build with correct flags (%%optflags)

* Tue Jul 10 2007 Mike Christie <mchristie@redhat.com> - 0.0-0.20070620snap
- first build
