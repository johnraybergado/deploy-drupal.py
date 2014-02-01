#!/usr/bin/python
import subprocess, getopt, sys, getpass, os

def main():
  print "executing deploy-drupal ..."
  
  ## check if required software (apache, mysql, php, drush) exists
  ## apache_check = subprocess.call('apache2')

  ## parse options and arguments
  try:
    options, arguments = getopt.getopt(sys.argv[1:], 'd:i:', ['drupal-path=', 'import='])
  except getopt.GetoptError as err:
    print str(err)
    print("Usage: %s --drupal-path /path/to/drupal --import /path/to/sql-dump (if importing from an existing installation)" % sys.argv[0])
    print("Or %s -d /path/to/drupal -i /path/to/sql-dump (if importing from an existing installation)" % sys.argv[0])
    sys.exit(2)

  drupal_path = ''
  sql_dump_path = ''
  for option, value in (options):
    if option in ('-d', '--drupal-path'):
  	  drupal_path = value
    elif option in ('-i', '--import'):
      sql_dump_path = value
    else:
      assert False, "unhandled option"

  ## create mysql databases for drupal
  mysql_user = raw_input("Enter mysql user: ")
  mysql_password = getpass.getpass("Enter password: ")
  database_name = raw_input("Enter name of database: ")
  print "creating mysql database..."
  subprocess.call(['mysqladmin', 'create', '%s' % database_name, '-u%s' % mysql_user, \
   '-p%s' % mysql_password])

  # recreate settings.php file
  # use default for the mean time
  site_folder_path = '%ssites/default/' % drupal_path;
  default_settings_dot_php = open('%sdefault.settings.php' % site_folder_path, 'r').read()
  settings_dot_php = open('%ssettings.php' % site_folder_path, 'w')
  settings_dot_php.truncate()
  settings_dot_php.write(default_settings_dot_php)
  settings_dot_php.close()

  ## change permissions of default folder and settings.php
  subprocess.call(['chmod', '-v', 'a+w', '%ssettings.php' % site_folder_path])
  subprocess.call(['chmod', '-v', 'a+w', site_folder_path])

  ## install drupal using drush
  print "installing drupal using drush..."
  original_directory = os.getcwd()
  os.chdir(drupal_path)
  subprocess.call(['drush', 'si', '--db-url=mysql://%s:%s@localhost/%s' \
  	% (mysql_user, mysql_password, database_name)])

  ## revert permissions of default folder and settings.php
  os.chdir(original_directory)
  subprocess.call(['chmod', '-v', '644', '%ssettings.php' % site_folder_path])
  subprocess.call(['chmod', '-v', '755', site_folder_path])

if __name__ == '__main__':
  main()