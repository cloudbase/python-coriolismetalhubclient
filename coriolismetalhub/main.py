import sys
import os

from cliff.app import App
from cliff.commandmanager import CommandManager

from coriolismetalhub import client


class CoriolisMetalApp(App):

    def __init__(self):
        super(CoriolisMetalApp, self).__init__(
            description='Coriolis metal CLI',
            version='0.1',
            command_manager=CommandManager('coriolismetalhub.cli'),
            deferred_help=True)

    def _env(self, var_name, default=None):
        return os.environ.get(var_name, default)

    def build_option_parser(self, description, version, argparse_kwargs=None):
        parser = super(CoriolisMetalApp, self).build_option_parser(
            description, version, argparse_kwargs)

        parser.add_argument(
            '--endpoint', '-e',
            default=self._env("CORIOLIS_METAL_ENDPOINT"),
            help='Coriolis Metal hub endpoint.')
        parser.add_argument(
            '--ca-cert',
            default=self._env("CORIOLIS_METAL_CA_CERT"),
            help='CA certificate.')
        parser.add_argument(
            '--client-cert', '-c',
            default=self._env("CORIOLIS_METAL_CLIENT_CERT"),
            help='Client certificate.')
        parser.add_argument(
            '--client-key', '-k',
            default=self._env("CORIOLIS_METAL_CLIENT_KEY"),
            help='Client certificate private key.')
        parser.add_argument('--no-auth', '-N', action='store_true',
                            help='Do not use authentication.')
        parser.add_argument('--os-identity-api-version',
                            metavar='<identity-api-version>',
                            default=self._env('OS_IDENTITY_API_VERSION', "3"),
                            help='Specify Identity API version to use. '
                            'Defaults to env[OS_IDENTITY_API_VERSION]'
                            ' or 3.')
        parser.add_argument('--os-auth-url', '-A',
                            metavar='<auth-url>',
                            default=self._env('OS_AUTH_URL'),
                            help='Defaults to env[OS_AUTH_URL].')
        parser.add_argument('--os-username', '-U',
                            metavar='<auth-user-name>',
                            default=self._env('OS_USERNAME'),
                            help='Defaults to env[OS_USERNAME].')
        parser.add_argument('--os-user-id',
                            metavar='<auth-user-id>',
                            default=self._env('OS_USER_ID'),
                            help='Defaults to env[OS_USER_ID].')
        parser.add_argument('--os-password', '-P',
                            metavar='<auth-password>',
                            default=self._env('OS_PASSWORD'),
                            help='Defaults to env[OS_PASSWORD].')
        parser.add_argument('--os-user-domain-id',
                            metavar='<auth-user-domain-id>',
                            default=self._env('OS_USER_DOMAIN_ID'),
                            help='Defaults to env[OS_USER_DOMAIN_ID].')
        parser.add_argument('--os-user-domain-name',
                            metavar='<auth-user-domain-name>',
                            default=self._env('OS_USER_DOMAIN_NAME'),
                            help='Defaults to env[OS_USER_DOMAIN_NAME].')
        parser.add_argument('--os-tenant-name', '-T',
                            metavar='<auth-tenant-name>',
                            default=self._env('OS_TENANT_NAME'),
                            help='Defaults to env[OS_TENANT_NAME].')
        parser.add_argument('--os-tenant-id', '-I',
                            metavar='<tenant-id>',
                            default=self._env('OS_TENANT_ID'),
                            help='Defaults to env[OS_TENANT_ID].')
        parser.add_argument('--os-project-id',
                            metavar='<auth-project-id>',
                            default=self._env('OS_PROJECT_ID'),
                            help='Another way to specify tenant ID. '
                                 'This option is mutually exclusive with '
                                 ' --os-tenant-id. '
                            'Defaults to env[OS_PROJECT_ID].')
        parser.add_argument('--os-project-name',
                            metavar='<auth-project-name>',
                            default=self._env('OS_PROJECT_NAME'),
                            help='Another way to specify tenant name. '
                                 'This option is mutually exclusive with '
                                 ' --os-tenant-name. '
                                 'Defaults to env[OS_PROJECT_NAME].')
        parser.add_argument('--os-project-domain-id',
                            metavar='<auth-project-domain-id>',
                            default=self._env('OS_PROJECT_DOMAIN_ID'),
                            help='Defaults to env[OS_PROJECT_DOMAIN_ID].')
        parser.add_argument('--os-project-domain-name',
                            metavar='<auth-project-domain-name>',
                            default=self._env('OS_PROJECT_DOMAIN_NAME'),
                            help='Defaults to env[OS_PROJECT_DOMAIN_NAME].')
        parser.add_argument('--os-auth-token',
                            metavar='<auth-token>',
                            default=self._env('OS_AUTH_TOKEN'),
                            help='Defaults to env[OS_AUTH_TOKEN].')
        return parser

    def prepare_to_run_command(self, cmd):
        cmd._cmd_options = self.options


def main(argv=sys.argv[1:]):
    myapp = CoriolisMetalApp()
    return myapp.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
