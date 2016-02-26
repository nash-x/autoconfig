__author__ = 'Administrator'
import ConfigParser
import os
import json
import errno
import shutil
import datetime
from jsonmerge import merge

CURRENT_DIR = os.path.split(os.path.realpath(__file__))[0]
NEW_CONFIG_DIR = os.sep.join([CURRENT_DIR, 'new_config'])

class AutoConfig(object):
    def __init__(self, config_files):
        """
        To do auto-config for set new option in new config file to old config file.
        We can think about that old config file is the original file in our system.
        One day, we want modify it, so we can rewrite a new cfg file which include options we want to set.
        Then we can use this AutoConfig to set it to system automaticlly.

        :param config_files: dict, key is old config file, value is new file.
        :return:
        """
        if type(config_files) != dict:
            raise TypeError('config files is not dict.')
        self.config_files = config_files

    def execute_config(self):
        for new_cfg_file_name, old_cfg_file in self.config_files.items():
            new_cfg_file = os.sep.join([NEW_CONFIG_DIR, new_cfg_file_name])
            self.config_file(old_cfg_file, new_cfg_file)

    def config_file(self, old_cfg_file, new_cfg_file):
        raise NotImplementedError()


class IniConfig(AutoConfig):

    def __init__(self, config_files):
        super(IniConfig, self).__init__(config_files)

    def config_file(self, old_cfg_file, new_cfg_file):
        old_cfg = ConfigParser.ConfigParser()
        old_cfg.read(old_cfg_file)
        new_cfg = ConfigParser.ConfigParser()
        new_cfg.read(new_cfg_file)

        old_cfg_sections = old_cfg.sections()
        new_cfg_sections = new_cfg.sections()

        #Deal with Same Section
        same_sections = [item for item in new_cfg_sections if item in old_cfg_sections]
        for section in same_sections:
            old_section_opts = old_cfg.options(section)
            new_section_opts = new_cfg.options(section)
            ret_opts = [item for item in new_section_opts if item not in old_section_opts]
            same_opts = [item for item in new_section_opts if item in old_section_opts]
            for modified_opt in same_opts:
                if not new_cfg.has_option('DEFAULT', modified_opt):
                    new_opt_value = new_cfg.get(section, modified_opt)
                    old_cfg.set(section, modified_opt, new_opt_value)
            for added_opt in ret_opts:
                if not new_cfg.has_option('DEFAULT', added_opt):
                    added_opt_value = new_cfg.get(section, added_opt)
                    old_cfg.set(section, added_opt, added_opt_value)

        # Deal with Added new Sections
        ret_sections = [item for item in new_cfg_sections if item not in old_cfg_sections]
        for added_section in ret_sections:
            added_opts = new_cfg.options(added_section)
            old_cfg.add_section(added_section)
            for added_opt in added_opts:
                if not new_cfg.has_option('DEFAULT', added_opt):
                    added_value = new_cfg.get(added_section, added_opt)
                    old_cfg.set(added_section, added_opt, added_value)

        # Deal with section "DEFAULT"
        new_defaults_opt = new_cfg.defaults()
        for key, value in new_defaults_opt.items():
            old_cfg.set('DEFAULT', key, value)

        old_cfg.write(open(old_cfg_file, 'w'))


class JsonConfig(AutoConfig):

    def __init__(self, config_files):
        super(JsonConfig, self).__init__(config_files)

    def config_file(self, old_cfg_file, new_cfg_file):
        with open(old_cfg_file, 'r') as ocf:
            data_old_cfg_file = json.load(ocf)
        with open(new_cfg_file, 'r') as ncf:
            data_new_cfg_file = json.load(ncf)
        cfg_dir = os.path.split(old_cfg_file)[0]
        file_name = os.path.split(old_cfg_file)[1]
        tmp_file = os.sep.join([cfg_dir, 'tmp_%s' % file_name])
        result = merge(data_old_cfg_file, data_new_cfg_file)

        with open(tmp_file, 'w') as tmp_f:
            tmp_f.write(json.dumps(result, indent=4))

        os.rename(tmp_file, old_cfg_file)


class SampleConfig(AutoConfig):

    def __init__(self, config_files):
        super(SampleConfig, self).__init__(config_files)

    def config_file(self, old_cfg_file, new_cfg_file):
        dst_dir = os.path.split(os.path.realpath(old_cfg_file))[0]
        self.copy_anything(new_cfg_file, dst_dir)

    def copy_anything(self, src, dst):
        try:
            shutil.copytree(src, dst)
        except OSError as exc:
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else:
                raise

class Backup(object):
    def __init__(self, backup_files, backup_dir):
        """

        :param backup_files: list, the list of backup files
        :return:
        """
        self.backup_files = backup_files
        self.backup_dir = backup_dir

    def copy_anything(self, src, dst):
        try:
            shutil.copytree(src, dst)
        except OSError as exc:
            if exc.errno == errno.ENOTDIR:
                shutil.copy(src, dst)
            else:
                raise

    def backup_file(self, file_full_name, backup_dir):
        self.copy_anything(file_full_name, backup_dir)

    def execute_backup(self):
        current_time = str(datetime.datetime.now())
        new_bak_dir = os.sep.join([self.backup_dir, current_time])
        os.mkdir(new_bak_dir)
        for b_f in self.backup_files:
            self.backup_file(b_f, new_bak_dir)


class ConfigMain(object):
    def __init__(self):
        self.current_dir = os.path.split(os.path.realpath(__file__))[0]
        self.backup_dir = os.sep.join([self.current_dir, 'backup'])
        self.cfg_file = os.sep.join([self.current_dir, 'autoconfig.json'])

        with open(self.cfg_file, 'r') as autoconfig_file:
            self.f_autoconfig = json.load(autoconfig_file)
            self.json_config_files = self.f_autoconfig.get('json')
            self.ini_config_files = self.f_autoconfig.get('ini')
            self.sample_config_files = self.f_autoconfig.get('sample')

    def _backup_files(self):
        backup_files = self.json_config_files.values() + \
                       self.ini_config_files.values() +\
                       self.sample_config_files.values()
        backup = Backup(backup_files, self.backup_dir)
        backup.execute_backup()

    def _autoconfig_json_files(self):
        json_autonconfig = JsonConfig(self.json_config_files)
        json_autonconfig.execute_config()

    def _autoconfig_ini_files(self):
        ini_autoconfig = IniConfig(self.ini_config_files)
        ini_autoconfig.execute_config()

    def _autoconfig_sample_files(self):
        sample_autoconfig = SampleConfig(self.sample_config_files)
        sample_autoconfig.execute_config()

    def execute(self):
        self._backup_files()
        self._autoconfig_json_files()
        self._autoconfig_ini_files()
        self._autoconfig_sample_files()

if __name__ == '__main__':
    config = ConfigMain()
    config.execute()


