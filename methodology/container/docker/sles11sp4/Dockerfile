############
#Base Image#
############
FROM suse/sles11sp4

################
#Proxy Settings#
################
ENV http_proxy http://proxy-chain.intel.com:911
ENV https_proxy http://proxy-chain.intel.com:912
ENV no_proxy intel.com,.intel.com,localhost,127.0.0.1,10.0.0.0/8,192.168.0.0/16,172.16.0.0/12

#############
#Repo Config#
#############
ADD repo-files/*.repo /etc/zypp/repos.d/
RUN zypper --no-gpg-checks --non-interactive addrepo -f -c http://download.opensuse.org/repositories/devel:/gcc/SLE-11/ gcc-repo
RUN zypper --no-gpg-checks --non-interactive ref

######################
#Package Installation#
######################
RUN zypper -n --no-refresh install -y curl
RUN zypper -n --no-refresh install -y m4
RUN zypper -n --no-refresh install -y ruby
RUN zypper -n --no-refresh install -y python
RUN zypper -n --no-refresh install -y libbz2-devel libcurl-devel libexpat-devel zlib-devel libelf-devel
RUN zypper -n --no-refresh install -y -t pattern Basis-Devel
RUN zypper -n --no-refresh install -y vim
RUN zypper -n --no-refresh install -y xorg-x11-libXpm
RUN zypper -n --no-refresh install -y ocaml
RUN zypper -n --no-refresh install -y util-linux
#RUN zypper -n --no-refresh install -y time
RUN zypper -n --no-refresh install -y make
#RUN zypper -n --no-refresh install -y kmod
#RUN zypper -n --no-refresh install -y openssl
RUN zypper -n --no-refresh install -y xorg-x11-xauth
#RUN zypper -n --no-refresh install -y vncmanager
RUN zypper -n --no-refresh install -y glibc-locale glibc-i18ndata
RUN zypper -n --no-refresh install -y krb5-devel krb5-client
RUN zypper -n --no-refresh install -y -f --force-resolution gcc6 gcc6-c++
RUN zypper -n --no-refresh install -y boost-devel
RUN zypper -n --no-refresh install -y strace
RUN zypper -n --no-refresh install -y samba-client
RUN zypper -n --no-refresh install -y tar
RUN zypper -n --no-refresh install -y zip
RUN zypper -n --no-refresh install -y guile
RUN zypper -n --no-refresh install -y libpng3
RUN zypper -n --no-refresh install -y gpm
RUN zypper -n --no-refresh install -y telnet
RUN zypper -n --no-refresh install -y glibc-32bit zlib libncurses5-32bit
RUN zypper -n --no-refresh install -y yp-tools ypbind nscd vasclnts
RUN zypper -n --no-refresh install -y sudo
RUN zypper -n --no-refresh install -y tcsh
RUN zypper -n --no-refresh install -y java-11-openjdk
RUN zypper -n --no-refresh install -y wget
RUN zypper -n --no-refresh install -y libreadline5
RUN zypper -n --no-refresh install -y libxml2
RUN zypper -n --no-refresh install -y libevent-1_4-2
RUN zypper -n --no-refresh install -y liblzma5
RUN zypper -n --no-refresh install -y xorg-x11-server
RUN zypper -n --no-refresh install -y libgcrypt11
RUN zypper -n --no-refresh install -y xorg-x11-fonts
RUN zypper -n --no-refresh install -y libbz2-1
RUN zypper -n --no-refresh install -y libbz2-1-32bit
RUN zypper -n --no-refresh install -y zlib-32bit
#RUN zypper -n --no-refresh install -y libopenssl0_9_8-32bit
RUN zypper -n --no-refresh install -y gpm-32bit
RUN zypper -n --no-refresh install -y libxml2-32bit

RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/network/SLE_15/ links_repo
RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/home:/lzwang:/DP:/libs/openSUSE_Leap_15.1/ libevent_links_dependent_repo
RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/Emulators:/Wine/SLE-12-SP3/ liblzma_links_dependent_repo
RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/OBS:/Server:/2.10/SLE_12_SP5/ libzstd_links_dependent_repo
RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/Archiving/SLE_15_SP1/ libbrotlidec1_links_dependent_repo
RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/distribution/leap/15.2/repo/oss/ Terminals:X11
RUN zypper --no-gpg-checks --non-interactive ref
RUN zypper -n --no-refresh install -y --force-resolution links

RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/X11:/windowmanagers/openSUSE_Leap_15.0/ WM:X11
RUN zypper --no-gpg-checks --non-interactive ref
RUN zypper -n --no-refresh in -f -y libncurses6
RUN zypper -n --no-refresh install -y -r Terminals:X11 xterm-bin
#RUN zypper -n --no-refresh dup -r WM:X11
RUN zypper -n --no-refresh in -f -y icewm
#RUN zypper -n --no-refresh install -y python36
RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/Java:/packages/SLE_15_SP1/ java_packages:eclipse
RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/Java:/bootstrap/SLE_12_SP5/ java_bootstrap:eclipse
RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/network:/utilities/SLE_12_SP4/ network_utilities
RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/home:/efagra:/SLE12/SLE_12/ libgif:eclipse 
RUN zypper --no-gpg-checks --non-interactive ref
RUN zypper -n --no-refresh rm openssl
#RUN zypper -n --no-refresh install -y -f --force-resolution --from java_packages:eclipse eclipse-platform

RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/devel:/tools:/scm/SLE_15/ Tools_SCM
RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/repositories/home:/sdrahn:/CS/SLE_11_SP4/ perl5.10:SCM
RUN zypper --no-gpg-checks --non-interactive ref -r Tools_SCM perl5.10:SCM
RUN zypper -n --no-refresh install --from Tools_SCM -y -f --force-resolution git
RUN zypper -n --no-refresh install -y --from Tools_SCM git-lfs
RUN zypper -n --no-refresh install -y tightvnc 
RUN zypper -n --no-refresh install -y xorg-x11-fonts-legacy

COPY texlive.profile /usr/app/
RUN mkdir /usr/app/texlive-2020 ; cd /usr/app/texlive-2020 ; wget --quiet -O - http://mirror.ctan.org/systems/texlive/tlnet/install-tl-unx.tar.gz | tar -C /usr/app/texlive-2020 -xz --strip-components=1 ;\
   sed -ie 's/https/http/g' /usr/app/texlive-2020/install-tl ; /usr/app/texlive-2020/install-tl --profile=/usr/app/texlive.profile

#RUN zypper --no-gpg-checks --non-interactive ar -f -c http://download.opensuse.org/tumbleweed/repo/oss tumbleweed:Python3.8.3
#RUN zypper --no-gpg-checks --non-interactive ref -r tumbleweed:Python3.8.3
#RUN zypper -n --no-refresh install -y --from tumbleweed:Python3.8.3 python3
###########
#Sym Links#
###########
RUN ln -s /nfs/site/proj /p
RUN ln -s /nfs/site/itools/em64t_SLES11 /usr/intel
RUN ln -s /usr/lib64/libxml2.so.2.9.4 /usr/lib64/libxml2.so
RUN ln -sf /usr/bin/gcc-6 /usr/bin/gcc
RUN ln -sf /usr/bin/g++-6 /usr/bin/g++
RUN ln -sf /usr/bin/python36 /usr/bin/python
RUN ln -s /usr/intel/pkgs/python3/3.7.4/bin/python3.7 /usr/bin/python3.7.4
#############
#Misc Config#
#############
COPY krb5.conf /etc/
#RUN localedef -c -i en_US -f UTF-8 en_US.UTF-8
RUN echo "simics_lab ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers
RUN mkdir /etc/sudo
RUN cp /etc/sudoers /etc/sudo/sudoers

##############
#ENV Settings#
##############
#ENV PATH "/usr/intel/bin:$PATH"
#ENV USER_ITOOLS "/home/simics_lab/.itools"
ENV PATH "$PATH:/nfs/site/disks/ssg_stc_simics_scratch/ssm_methodology/releases/tools/linux/devel/bin"
ENV LM_LICENSE_FILE "84300@fmylic7005.fm.intel.com:84300@inllic08.iind.intel.com"
RUN mkdir -p /usr/share/wallpapers/openSUSEdefault/contents/images;\
    wget --no-check-certificate https://www.suse.com/assets/img/museum/wallpaper/suse_wallpaper-A_1920x1080.jpg -O /usr/share/wallpapers/openSUSEdefault/contents/images/1920x1080.jpg

##########################
#User and Group Additions#
##########################
RUN groupadd ssdv -g 38727
RUN groupadd tgl_simics -g 20091
RUN useradd -m -d /nfs/site/home/simics_lab -s /bin/bash -g 38727 -G 100 -G 20091 -u 31647 simics_lab
#RUN mkdir -p /home/simics_lab/.ssh
#COPY ssh_config /home/simics_lab/.ssh/config
#COPY simics_artifactory_config.json /home/simics_lab
#COPY .itools /home/simics_lab/
#RUN chown simics_lab /home/simics_lab/ -R

#########
#Scripts#
#########
RUN mkdir -p /usr/app
COPY entrypoint.sh /usr/app
COPY build.sh /usr/app
COPY vncserver.sh /usr/app
COPY build-make-doc.py /usr/app
RUN chmod +x /usr/app/*.sh

##############
#Expose Ports#
##############
#ENV DISPLAY=:1 \
#    VNC_PORT=5901 \
#    NO_VNC_PORT=6901
#EXPOSE $VNC_PORT $NO_VNC_PORT

#############
#User Switch#
#############
#USER simics_lab

############
#Entrypoint#
############
CMD ["/bin/bash"]

