import subprocess
import re
import sys
import json
import os

def main():
  proc = subprocess.Popen(["curl", "-s", "http://downloads.vagrantup.com"], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  #print out

  dl_pages = re.findall('(?<=a class=\"tag\" href=\").*(?=\".*)', out)
  #print dl_pages

  for page in dl_pages:
    version = re.search('(?<=tags/)v\d{1,2}\.\d{1,2}\.\d{1,2}', page).group(0)
    urls = fetchDownloadUrls(page)
    for url in urls:
      fetchPackage(url,version)
  buildPackageFiles()
  buildReleaseFiles()

  return 0

def fetchDownloadUrls(page):
  proc = subprocess.Popen(["curl", "-s", page], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  #print out

  dl_links = re.findall('(?<=a class=\"file type-deb\" href=\").*(?=\".*)', out)
  #print dl_links
  return dl_links

def fetchPackage(url,version):
  if version.find('.0.') > 0:
    stable='stable'
  else:
    stable='unstable'
  if url.find('amd64') > 0:
    arch = "amd64"
  elif url.find('x86_64') > 0:
    arch = "amd64"
  else:
    arch = "i386"
  v = version.replace('v',"")
  dirname = "/var/www/vagrant/pool/main/v/vagrant-"+stable+"/"
  filename = "vagrant_" + v + "_" + arch + ".deb"
  
  if not os.path.isfile(dirname+filename):
    try:
      os.makedirs(dirname)
    except:
      True 
    proc = subprocess.Popen(["wget", "-O",dirname+filename, url], stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
  #print out

  return filename 

def buildPackageFiles():
  os.chdir("/var/www/vagrant")
  deb_path = "pool/main/v/vagrant-stable"
  proc = subprocess.Popen(["dpkg-scanpackages", "-m","-a", "amd64", deb_path], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  fh = open("/var/www/vagrant/dists/stable/main/binary-amd64/Packages",'w')
  fh.write(out)
  proc = subprocess.Popen(["dpkg-scanpackages", "-m","-a", "i386", deb_path], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  fh = open("/var/www/vagrant/dists/stable/main/binary-i386/Packages",'w')
  fh.write(out)
  deb_path = "pool/main/v/vagrant-unstable"
  proc = subprocess.Popen(["dpkg-scanpackages", "-m","-a", "amd64", deb_path], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  fh = open("/var/www/vagrant/dists/unstable/main/binary-amd64/Packages",'w')
  fh.write(out)
  proc = subprocess.Popen(["dpkg-scanpackages", "-m","-a", "i386", deb_path], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  fh = open("/var/www/vagrant/dists/unstable/main/binary-i386/Packages",'w')
  fh.write(out)


def buildReleaseFiles():
  header="""
Origin: Unofficial Vagrant Packages
Label: Unofficial Vagrant Packages
Codename: stable
Date: Thurs, 5 Sep 2013 07:27:37 UTC
Architectures: i386 amd64
Components: main
Description: Vagrant APT Repository
MD5Sum:
"""
  file_64 = "/var/www/vagrant/dists/stable/main/binary-amd64/Packages"
  size_64 = os.stat(file_64).st_size
  proc = subprocess.Popen(["md5sum", file_64], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  md5_64 = out.split()[0]
  proc = subprocess.Popen(["sha256sum", file_64], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  sha256_64 = out.split()[0] 
  file_32 = "/var/www/vagrant/dists/stable/main/binary-i386/Packages"
  size_32 = os.stat(file_32).st_size
  proc = subprocess.Popen(["md5sum", file_32], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  md5_32 = out.split()[0]
  proc = subprocess.Popen(["sha256sum", file_32], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  sha256_32 = out.split()[0]
  fh = open("/var/www/vagrant/dists/stable/Release.tmp",'w')
  fh.write(header)
  fh.write(" "+md5_64+" "+str(size_64)+" "+file_64.replace("/var/www/vagrant/dists/stable/",""))
  fh.write("\n "+md5_32+" "+str(size_32)+" "+file_32.replace("/var/www/vagrant/dists/stable/",""))
  fh.write("\nSHA256:\n")
  fh.write(" "+sha256_64+" "+str(size_64)+" "+file_64.replace("/var/www/vagrant/dists/stable/",""))
  fh.write("\n "+sha256_32+" "+str(+size_32)+" "+file_32.replace("/var/www/vagrant/dists/stable/",""))
  fh.close()
  proc = subprocess.Popen(["cp", "/var/www/vagrant/dists/stable/Release.tmp", "/var/www/vagrant/dists/stable/Release"], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  file_64 = "/var/www/vagrant/dists/unstable/main/binary-amd64/Packages"
  size_64 = os.stat(file_64).st_size
  proc = subprocess.Popen(["md5sum", file_64], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  md5_64 = out.split()[0]
  proc = subprocess.Popen(["sha256sum", file_64], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  sha256_64 = out.split()[0]
  file_32 = "/var/www/vagrant/dists/unstable/main/binary-i386/Packages"
  size_32 = os.stat(file_32).st_size
  proc = subprocess.Popen(["md5sum", file_32], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  md5_32 = out.split()[0]
  proc = subprocess.Popen(["sha256sum", file_32], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()
  sha256_32 = out.split()[0]
  fh = open("/var/www/vagrant/dists/unstable/Release.tmp",'w')
  fh.write(header)
  fh.write(" "+md5_64+" "+str(size_64)+" "+file_64.replace("/var/www/vagrant/dists/unstable/",""))
  fh.write("\n "+md5_32+" "+str(size_32)+" "+file_32.replace("/var/www/vagrant/dists/unstable/",""))
  fh.write("\nSHA256:\n")
  fh.write(" "+sha256_64+" "+str(size_64)+" "+file_64.replace("/var/www/vagrant/dists/unstable/",""))
  fh.write("\n "+sha256_32+" "+str(+size_32)+" "+file_32.replace("/var/www/vagrant/dists/unstable/",""))
  fh.close()
  proc = subprocess.Popen(["cp", "/var/www/vagrant/dists/unstable/Release.tmp", "/var/www/vagrant/dists/unstable/Release"], stdout=subprocess.PIPE)
  (out, err) = proc.communicate()


def addVersion(version,page):
  urls = fetchDownloadUrls(page)
  for url in urls:
    fetchPackage(url,version)
  buildPackageFiles()
  buildInReleaseFiles()
  addJson(version)



if __name__ == "__main__":
    sys.exit(main())


