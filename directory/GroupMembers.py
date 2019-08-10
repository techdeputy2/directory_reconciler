from __future__ import print_function

def list(email, dirclient, members_only):
    roleFilter = ['MEMBER'] if members_only else None
    results = dirclient.members().list(groupKey=email, roles=roleFilter).execute()
    memberList = []

    while True:
        members = results.get('members', [])
        if members:
            memberList.extend([m['email'] for m in members])
        if not 'nextPageToken' in results:
            break
        else:
            token = results['nextPageToken']
            results = dirclient.members().list(groupKey=email, pageToken=token,roles=roleFilter).execute()
    memberList = [m.lower() for m in memberList]
    return memberList