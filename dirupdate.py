from __future__ import print_function
import pickle
import os.path
import argparse
import sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from directory import GroupMembers
from sheets.CSVDirectory import CSVDirectory
from resolver.MailResolver import MailResolver

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/admin.directory.group']

ALWAYS_MEMBERS = ['boosterleaders@vhsband.com', 'execboard@vhsband.com', 'mulch@vhsband.com', 'bandstaff@vhsband.com']

SHEET_OPTIONS = [['9', True, True], ['9', True, False], ['9', False, True], ['9', False, False],
                 ['10', True, True], ['10', True, False], ['10', False, True], ['10', False, False],
                 ['11', True, True], ['11', True, False], ['11', False, True], ['11', False, False],
                 ['12', True, True], ['12', True, False], ['12', False, True], ['12', False, False]]

MAILING_LISTS = [
    'freshmen-b-students@vhsband.com', 'freshmen-b-parents@vhsband.com', 'freshmen-v-students@vhsband.com',
    'freshmen-v-parents@vhsband.com', 'sophomore-b-students@vhsband.com', 'sophomore-b-parents@vhsband.com',
    'sophomore-v-students@vhsband.com', 'sophomore-v-parents@vhsband.com',
    'junior-b-students@vhsband.com', 'junior-b-parents@vhsband.com', 'junior-v-students@vhsband.com',
    'junior-v-parents@vhsband.com', 'senior-b-students@vhsband.com', 'senior-b-parents@vhsband.com',
    'senior-v-students@vhsband.com', 'senior-v-parents@vhsband.com']


def args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--report', help="Report mode, displays differences", action="store_true")
    parser.add_argument('-g', '--generate',
                        help="Generate mode, generates missing mailing list entries as an import CSV",
                        action="store_true")
    parser.add_argument('-v', '--validate',
                        help="Validation mode, generates a list of invalid (based on MX domain) email addresses",
                        action="store_true")
    return parser


def build_google_api():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('admin', 'directory_v1', credentials=creds)
    return service


def process_lists(report_mode, generate_mode, validate_mode):
    service = build_google_api()
    csv = CSVDirectory('directory.csv')
    mx_resolver = MailResolver()

    for index, mailing_list in enumerate(MAILING_LISTS):
        args = SHEET_OPTIONS[index]
        mailing_members = set(GroupMembers.list(mailing_list, service, True))
        directory_members = set(csv.list(args[0], args[1], args[2]))
        directory_members.update(ALWAYS_MEMBERS)

        print('\n--------------------------------------------\n')
        print(mailing_list)
        missing_mailing = directory_members - mailing_members
        if len(missing_mailing) > 0:
            if report_mode:
                print('In directory but not in mailing list:')
                print(missing_mailing)
            elif generate_mode:
                print('CSV for import as follows\n\n')
                print('Group Email [Required],Member Email,Member Type,Member Role')
                for m in missing_mailing:
                    print('{0},{1},USER,MEMBER'.format(mailing_list, m))
                print('\n\n')
            elif validate_mode:
                for m in missing_mailing:
                    if not mx_resolver.check_email(m):
                        print('{0} does not appear to be from a valid email domain'.format(m))
        else:
            print('All directory entries are in the mailing list')

        missing_directory = mailing_members - directory_members
        if len(missing_directory) > 0:
            print('In mailing list but not in directory:')
            print(missing_directory)
        else:
            print('All mailing list entries are in the directory (minus the ones that are in every mailing list, e.g. execboard, bandstaff, etc')
        print('\n--------------------------------------------\n')


def main():
    assert len(SHEET_OPTIONS) == len(MAILING_LISTS), 'Inconsistent number of sheet options to mailing lists'
    parser = args_parser()
    args = parser.parse_args()

    if args.report and args.generate and args.validate:
        print("Only one of report, generate or validate mode is allowed")
        parser.print_help()
        sys.exit()

    if not args.report and not args.generate and not args.validate:
        print("Must choose a mode, report, validate, or generate")
        parser.print_help()
        sys.exit()

    process_lists(args.report, args.generate, args.validate)


if __name__ == '__main__':
    main()
