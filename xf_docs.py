#! C:\Users\assen_bankov\PycharmProjects\xf_documentation\app\ve\Scripts\python.exe

"""
Created on Wed Nov  8 07:36:33 2017

@author: aceh40
"""

import requests
import os
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
import settings
from site_scanner import site_scanner
from logger import logger, start_time
from file_scanner import file_dict

# =============================================================================
# Basic Variables
# =============================================================================

home_page = settings.HOME_PAGE

# Login credentials:
login_cred = dict(username=settings.USER, password=settings.PASSWORD)

# Regex to use to find whether I need to log in or not:
login_page_regex = re.compile(r'(sso)(\.)({})(\.)(com)'.format(settings.LOGIN_PAGE_REGEX))
home_page_regex = re.compile(r'(support)(\.)({})(\.)(com)'.format(settings.HOME_PAGE_REGEX))

# =============================================================================
#      Support Document class definition
# =============================================================================


class DatasetPage(object):
    """ Represents a page with document links to a data set (Financials, Estimates etc.)

        Methods:
            - init
            - Find all document links
    """

    def __init__(self, dataset_page_link):
        """
        Identified by its link. I can add
        :param dataset_page_link:
        """
        self.dataset_page_link = dataset_page_link

    @staticmethod
    def get_all_links(self, session):
        """
            :return: all links from a dataset page stored in a file / pickle / dict?
        """

        home_page_content = session.get (home_page)  # go to home page
        home_page_soup = BeautifulSoup(home_page_content.text, 'lxml')  # Parse the html
        home_links = home_page_soup.select('li a')    # look for these tags
        print('\nParsed home page using <li>, <a> tags & got:')
        for i in range(0, len(home_links)):  # show results. NOT NEEDED.
            print('\n' + str(home_links[i].getText()) + '\t' + str(home_links[i].attrs))
        dataset_pages = home_page_soup.select('tbody a')
        print('\nParsed home page using <tbody>, <a> tags & got:')
        for j in dataset_pages:
            print(str(j.getText()) + '\t' + str(j.attrs))


class SupportDocument(object):
    """ SupportDocument will represent an individual document with the following attributes:
            - source_link - Link on the support site
            - target_dir - local directory
            - original_name - name as it appears on the site
            - preferred_name - name to use when downloading locally. Can be null.
        Methods:
            - download
            - initialize?
     """
    #source_link: object

    def __init__(self, source_link, original_name, target_dir, preferred_name=''):
        self.source_link = source_link
        self.original_name = original_name
        self.target_dir = str(target_dir)
        self.preferred_name = str(preferred_name)
        logger.debug('Source Document source link: {}'.format(self.source_link))
        logger.debug('Source Document original name: {}'.format(self.original_name))
        logger.debug('Source Document target directory: {}'.format(self.target_dir))
        logger.debug('Source Document preferred name: {}'.format(self.preferred_name))

    def get_full_url(self):
        """concatenate the source_link to the home_page
        """
        full_url = home_page + self.source_link
        return full_url

    def get_target_name(self):
        """ Get the original name if preferred name is missing.
            :return:
        """
        if self.preferred_name is None:
            target_name = self.original_name
        elif len(self.preferred_name) > 4:
            target_name = self.preferred_name
        else:
            target_name = self.original_name
        logger.debug('Source Document target file name: {}'.format(target_name))
        return target_name

    def get_target_full_dir(self):
        """
        :return: the full path where the file will be downloaded.
        """
        file_name = self.get_target_name()
        if self.target_dir is not None and len(self.target_dir) > 3:
            target_full_dir = self.target_dir
        elif file_name in file_dict.keys():
            target_full_dir = file_dict[file_name]
        else:
            target_full_dir = settings.DEFAULT_DOC_DIR
        return target_full_dir
    #~TODO: See how you can save the detected directory back to the excel file. Is the file even necessary, except for preferred name?

    def download(self, session):
        """ Opens request.Session, tries to log in, and downloads the files.
        :return:
        """
        target_path = self.get_target_full_dir()
        os.chdir(target_path)
        schema_get = session.get(self.get_full_url(), verify=False)
        target_name = self.get_target_name()
        logger.debug('Starting download of file {} to {}.'.format(target_name.upper(), target_path))
        with open(os.path.join(target_path, target_name), "wb") as code:
            code.write(schema_get.content)
        logger.info('{} file has been downloaded successfully.'.format(target_name.upper()))


def authenticate(session):
    """ follows logic to authenticate on the site
    """
    r = session.get(settings.HOME_PAGE)
    logger.info('Redirected to: {}'.format(r.url))

    mo = login_page_regex.search(r.url)
    logger.info("Login regex result: {}".format(mo))
    if mo is not None:  # You are taken to the login page and need to login
        logger.info("Redirected to login page.")
        session.post(r.url, data=login_cred, verify=False)
        logger.info("Login response [{}]: {}".format(r.status_code, settings.HTTP_STATUS_CODES[r.status_code]))
        r.raise_for_status()
    else:
        mo = home_page_regex.search(r.url)
        logger.info("Redirected to home page.")
        if mo is not None:  # You are taken to the support home page and do not need to log in.
            logger.info('Already logged in.')
        else:
            logger.error("Redirected to unexpected URL.")
            logger.error("URL: {}".format(r.url))


# =============================================================================
#   MAIN:
# =============================================================================


def main():
    """

    :return:
    """
    doc_count = 0
    with requests.Session() as s:
        authenticate(s)
        site_scanner(s)
        df = pd.read_excel(io=settings.DATA_FILE, sheet_name='Sheet1', usecols='A:D')
        logger.info("Opening data file {}.".format(settings.DATA_FILE))
        dfx = df.tail(5)
        for i in df.index:
            source_link = df.iloc[i, 1]
            original_name = df.iloc[i, 0]
            new_name = df.iloc[i, 2]
            target_dir = df.iloc[i, 3]
            doc = SupportDocument(source_link, original_name, target_dir, new_name)
            logger.debug("Preparing to download of file {}...".format(original_name.upper()))
            doc.download(s)
            doc_count += 1

    end_time = datetime.now()
    runtime_format = '%H:%M:%S'
    run_time = end_time - start_time
    logger.info('{} files successfully downloaded.'.format(doc_count))
    logger.info('Task completed in {}'.format(str(run_time)))
    logger.info('---------------------------------------------------------------')
    logger.info('---------------------- PROGRAM END ----------------------------')
    logger.info('---------------------------------------------------------------')



main()