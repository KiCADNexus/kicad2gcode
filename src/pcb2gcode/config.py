#!/usr/bin/env python3

#
# If a file does not exist, create it and load it.
# The default path
#
import jsonschema
import logging

from constants import CONFIG_USER_PATH
from pathlib import Path

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.error import CommentMark

logger = logging.getLogger(__name__)

if not hasattr(CommentedMap, "yaml_set_comment_before_key"):
    def override_set_comment_before_key(self, key, comment, column=None, clear=False):
        """
        append comment to list of comment lines before key, '# ' is inserted
            before the comment
        column: determines indentation, if not specified take indentation from
                previous comment, otherwise defaults to 0
        clear: if True removes any existing comments instead of appending
        """
        key_comment = self.ca.items.setdefault(key, [None, [], None, None])
        if clear:
            key_comment[1] = []
        comment_list = key_comment[1]
        if comment:
            comment_start = '# '
            if comment[-1] == '\n':
                comment = comment[:-1]  # strip final newline if there
        else:
            comment_start = '#'
        if column is None:
            if comment_list:
                 # if there already are other comments get the column from them
                column = comment_list[-1].start_mark.column
            else:
                column = 0
        start_mark = CommentMark(column)
        comment_list.append(ruamel.yaml.tokens.CommentToken(
            comment_start + comment + '\n', start_mark, None))
        return self

    CommentedMap.yaml_set_comment_before_key = override_set_comment_before_key


class YamlConfigManager:
    """
    The manager does the following:
     - It opens a schema file (and checks it)
     - It tries to open a configuration file
     - If opens OK - tries to parse it then validate the content against the schema.
     -   If it validates - It returns the content as a Python object
     -   Else,
            it renames the config file
            Tries to generates a new default content based on the schema file
     -      it returns the default content
    """
    @staticmethod
    def _populate_defaults(schema):
        retval = None

        if 'default' in schema:
            retval = schema['default']
        elif 'const' in schema:
            retval = schema['const']
        elif 'type' in schema and schema['type'] == 'object':
            default_obj = CommentedMap()

            for prop_name, prop_schema in schema.get('properties', {}).items():
                default_value = __class__._populate_defaults(prop_schema)
                default_obj[prop_name] = default_value

            retval = default_obj
        elif 'type' in schema and schema['type'] == 'array':
            default_array = CommentedSeq()

            if 'items' in schema:
                default_item = __class__._populate_defaults(schema['items'])
                default_array.append(default_item)

            retval = default_array

        return retval

    @staticmethod
    def _add_comments(node, schema, add_comment=None, indent=0):
        """
        Given the fully formed node, add comments using the schema description
        """
        if 'description' in schema:
            desc = schema['description']

            if node and isinstance(node, CommentedMap):
                node.yaml_set_start_comment(desc, indent)

            if add_comment:
                print(desc)
                add_comment(desc)

        if schema.get('type') == 'object':
            for prop_name, prop_schema in schema.get('properties', {}).items():
                # Create a lambda for adding the comment
                if isinstance(node[prop_name], CommentedMap):
                    add_comment = lambda before: node.yaml_set_comment_before_after_key(prop_name, None, 0, before, 0)
                else:
                    print("XXX", prop_name)
                    add_comment = lambda before: node.yaml_set_comment_before_key(prop_name, before)

                if prop_name in node:
                    __class__._add_comments(node[prop_name], prop_schema, add_comment, indent+2)

        if 'type' in schema and schema['type'] == 'array':
            if 'items' in schema:
                __class__._add_comments(node[0], schema['items'], None, indent+2)


    def load_schema(self):
        import sys
        from importlib import resources
        from constants import SCHEMA_FILE__FILENAME_SUFFIX, SCHEMA_PATH

        self.schema_file_path = SCHEMA_PATH / Path(self.section_name + SCHEMA_FILE__FILENAME_SUFFIX)

        if not self.schema_file_path.exists():
            logger.critical("Missing schema file: %s", self.schema_file_path)
            raise RuntimeError("Corrupt package")

        try:
            with open(self.schema_file_path, 'r', encoding="utf-8") as self.schema_file_path:
                schema = ruamel.yaml.YAML().load(self.schema_file_path)
                validator = jsonschema.Draft7Validator(schema)
        except Exception as exception:
            logger.critical("Failed to process the schema file: %s", self.schema_file_path)
            logger.error("Got: %s", exception)
            raise RuntimeError(exception) from exception

        # The schema must be error free
        return schema, validator

    def load_content(self):
        retval = {}

        try:
            if not self.config_file_path.exists():
                logger.info("Configuration file '%s' is missing and will be created.", self.config_file_path)
                return retval
        except PermissionError:
            logger.info("Configuration file '%s' cannot be accessed.", self.config_file_path)
            return retval

        # Parse it!
        try:
            with open(self.config_file_path) as stream:
                retval = ruamel.yaml.round_trip_load(stream)
                jsonschema.validate(retval, self.schema)

                for key, value in retval.items():
                    pass

            return retval
        except OSError:
            logger.error("File '%s' could not be opened!", self.config_file_path)
        except ruamel.yaml.YAMLError as exception:
            logger.error("File '%s' is not a valid Yaml document!", self.config_file_path)
            logger.error(e)
        except jsonschema.ValidationError as exc:
            logger.error("File '%s' is not structured correctly!", self.config_file_path)
            logger.info("Details:\n%s", exc)
        except Exception as exception:
            logger.error("Failed to interpret the content of '%s'", self.config_file_path)
            logger.error("Got: %s", exception)

        # Since we failed to include the file succesfully, rename this one to make room for a fresh one
        newname = self.config_file_path.with_suffix(".yaml.old")

        try:
            self.config_file_path.replace(newname)
            logger.warning("Renaming the file %s", newname)
        except Exception as exception:
            logger.error("Failed to rename the file '%s' to '%s'", self.config_file_path, newname)
            logger.error("Got: %s", exception)

        return retval

    def generate_default_content(self):
        # Generate a default content
        default_config = self._populate_defaults(self.schema)
        self._add_comments(default_config, self.schema)

        return default_config

    def write_content(self):
        # Overwrite the file
        # Make sure the directory exists
        config_dir = self.config_file_path.parent

        if not config_dir.exists():
            try:
                config_dir.mkdir(0o0755, True, True)
            except Exception as exception:
                logger.error("Failed to create the directory '%s'", config_dir)
                logger.error("Got: %s", exception)

                # File won't be created
                return

        try:
            with open(self.config_file_path, 'w') as content_file:
                ruamel.yaml.round_trip_dump(self.content, content_file, Dumper=ruamel.yaml.RoundTripDumper)
        except Exception as exception:
            logger.error("Failed to create a default configuration file '%s'", self.config_file_path)
            logger.error("Got: %s", exception)

    def __init__(self, section_name: str) -> dict:
        """
        Create an instance of a Yaml configuration manager
        This manager is reponsible for processing a given Yaml configuration file.
        Doing so, guarantees a content to the caller.
        If the configuration file exists, it is parsed and checked against a schema.
        On errors, the file is renamed, an error generated, and a new file is created using the
        default values.

        @param section_name The name of section of configuration to handle such as 'racks'
        """
        from os.path import expanduser
        from constants import CONFIG_USER_PATH

        self.section_name = section_name
        self.config_file_path = Path(
            expanduser(CONFIG_USER_PATH) / Path(section_name + ".yaml")
        )

        self.schema, self.validator = self.load_schema()
        self.content = self.load_content()

        if self.content == {}:
            self.content = self.generate_default_content()
            self.write_content()

    def get_content(self):
        return self.content


class Config:
    def __init__(self) -> None:
        from constants import CONFIG_SECTIONS

        for section in CONFIG_SECTIONS:
            yaml_config = YamlConfigManager(section)

            # Multiword sections should be abreviated. Global settings becomes gs
            if '_' in section:
                section = ''.join([word[0] for word in section.split('_')])

            # Add to the config object
            setattr(self, section, yaml_config.get_content())

if __name__ == "__main__":
    import logging
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

# Create a unique config instance
config = Config()
