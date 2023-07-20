from __future__ import print_function
import logging
import time
import random
import googleapiclient

class GroupMembers:
    def __init__(self, email, dirclient, ignore_owners=True):        
        self.logger = logging.getLogger('GroupMembers')        
        self.api_queue = []        
        self.__build_list(email, dirclient, ignore_owners)
        

    def __build_list(self, email, dirclient, ignore_owners=True):
        self.logger.debug("__build_list")
        self.members = dirclient.members()
        self.group = email

        results = self.members.list(groupKey=email, maxResults=200).execute()       
        memberList = []

        while True:
            members = results.get('members', [])
            #filter here through list comprehension because the role filter doesn't seem to be working
            if members:
                if ignore_owners:
                    memberList.extend([m['email'] for m in members if m['role'] != 'OWNER'])
                else:
                    memberList.extend([m['email'] for m in members])
            if not 'nextPageToken' in results:
                break
            else:
                token = results['nextPageToken']
                results = dirclient.members().list(groupKey=email, maxResults=200, pageToken=token).execute()
        memberList = [m.lower() for m in memberList]
        self.memberList = memberList

    def list(self):
        return self.memberList

    def __batch_callback(self, request_id, response, exception):
        if exception is not None:
            self.logger.error('error with request {0}'.format(request_id))                          
            self.logger.error(exception)
            self.logger.error(type(exception))
            if isinstance(exception, googleapiclient.errors.HttpError):
                if exception.resp.status == 400:
                    self.logger.debug('Request failed, likely invalid input')                    
                elif exception.resp.status == 403:
                    self.logger.debug('Request failed, either due to permission or rate limiting, retrying...')
                    self.api_queue.append(request_id)


    def add_members(self, new_members, dirclient):
        self.logger.info("Adding {0} new members to {1}".format(len(new_members), self.group))
        self.api_queue.clear()
        self.api_queue.extend(new_members)
        
        for delay in [0, 1, 2, 4, 8, 16]:
            batch = dirclient.new_batch_http_request()
            if len(self.api_queue) < 1:
                self.logger.info("no more api requests to process")
                break
            sleeptime = delay + random.randrange(100, 1000) / 1000.0 
            self.logger.debug("sleeping {0} before making more api requests".format(sleeptime))
            time.sleep(sleeptime)
            for m in self.api_queue:
                new_member = {'email': m, 'role': 'MEMBER'}
                batch.add(self.members.insert(groupKey=self.group, body=new_member), request_id=m, callback=self.__batch_callback)
            self.api_queue.clear()
            self.logger.debug("Calling batch")
            batch.execute()
        if len(self.api_queue) > 0:
            self.logger.error("Failed after multiple retries to add members {0} to {1}".format(self.api_queue, self.group))

    def clear_members(self, dirclient):
        log = logging.getLogger()
        log.setLevel(logging.DEBUG)
        log.info('Clearing all MEMBER role members from group {0}'.format(self.group))
        self.api_queue.clear()
        self.api_queue.extend(self.memberList)
    
        for delay in [0, 1, 2, 4, 8, 16, 32]:
            batch = dirclient.new_batch_http_request()
            if len(self.api_queue) < 1:
                log.info("no more api requests to process")
                break
            sleeptime = delay + random.randrange(100, 1000) / 1000.0 
            log.debug("sleeping {0} before making more api requests".format(sleeptime))
            time.sleep(sleeptime)
            for m in self.api_queue:
                log.debug('Removing {0} from {1}'.format(m, self.group))
                batch.add(self.members.delete(groupKey=self.group, memberKey=m), request_id=m, callback=self.__batch_callback)            
            self.api_queue.clear()
            self.logger.debug("Calling batch")
            batch.execute()

        if len(self.api_queue) > 0:
            log.error("Failed after multiple retries to clear members {0} from {1}".format(self.api_queue, self.group))

        log.debug("Rebuilding membership list")
        self.__build_list(self.group, dirclient, ignore_owners=True)