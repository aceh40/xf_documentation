import settings
import os
import re
import requests
import pandas as pd
from bs4 import BeautifulSoup
from logger import logger


login_cred = dict(username=settings.USER, password=settings.PASSWORD)
columns = ['link', 'file_name', 'new_name', 'target_dir']


def get_main_body_link_list(html):
    """ get main body html of a page.
    :return:
    """
    soup = BeautifulSoup(html, 'lxml')
    """ Added site scanner - looks up all links on the site and checks if they are support docs.
    """
    logger.debug('Setting up BeautifulSoup object...')
    main_body = soup.find(id='main-col')
    link_list = main_body.find_all('a')
    logger.debug('Found {} links.'.format(len(link_list)))
    return link_list



def get_file_name_from_link(url):
    """ Get the file name from a link.

    :param url:
    :return:
    """
    file_name_regex = re.compile(r'([^/]*$)')
    logger.debug('Extracting file name from link {}...'.format(url))
    mo = file_name_regex.search(url)
    if mo is not None:
        logger.debug('File name {} extracted.'.format(str(mo.group(0)).upper()))
    logger.debug('Extracting file name from link...')
    mo = file_name_regex.search(url)
    if mo is not None:
        logger.debug('File name {} extracted.'.format(upper(mo.group(0))))
        return mo.group(0)
    else:
        return ''


def load_data_file():
    """ Get the excel file into a data frame.
    :return: pandas DataFrame
    """
    df = pd.read_excel(io=settings.DATA_FILE, sheet_name='XpressfeedDocs', usecols='A:D')
    logger.info('Pandas DataFrame loaded from {}.'.format(os.path.split(settings.DATA_FILE)[1]))
    return df


def is_document(url):
    """ Checks if the link is for a document
    """
    doc_regex = re.compile(r'(\.)(pdf|xls|xlsx)$')  # check if it is a document link.
    mo = doc_regex.search(url)
    if mo is None:
        return False
    else:
        return True


def site_scanner(session):
    """ Scan the website for all useful links.
    :return:
    """
    df = load_data_file()
    df_list = list(df.link)
    new_item_list = []
    # print(df_list)
    # r = s.get(settings.HOME_PAGE)
    # s.post(r.url, data=login_cred, verify=False)    # log in the redirected login page
    r = session.get(settings.HOME_PAGE)       # go back to home page
    logger.debug('Scanning page "{}".'.format(r.url))
    dataset_link_list = get_main_body_link_list(r.text)     #get the list of links in main body.
    for dataset_link in dataset_link_list:
        dataset_url = settings.HOME_PAGE + dataset_link.get('href')     # contatenate the link to get url
        rr = session.get(dataset_url)     # get the page of the dataset link.
        if rr.status_code == 200:   # there are a few links that response 404
            logger.debug('Scanning page "{}".'.format(rr.url))
            document_link_list = get_main_body_link_list(rr.text)   # get the links within the dataset page
            for document_link in document_link_list:
                document_url = document_link.get('href')
                document_full_url = settings.HOME_PAGE + document_url   # get the url of the link
                if is_document(document_full_url) is True:
                    if document_url not in df_list:
                        new_item_list.append(document_url)
    logger.info('Found a total of {} new documents.'.format(len(new_item_list)))
    # print(len(new_item_list))
    link_list = []
    name_list = []
    for item in new_item_list:
        file_name = get_file_name_from_link(item)
        logger.debug('Extracted file name {} from new document URL.'.format(file_name))
        link_list.append(item)
        name_list.append(file_name)
        logger.debug('Appended new document name and URL to new document lists.')
    df_new = pd.DataFrame({'link': link_list,
                           'file_name': name_list
                           })
    logger.info('Concatenated new items DataFrame with main DataFrame.')
    concat = pd.concat([df, df_new], ignore_index=True)
    concat.to_excel(settings.DATA_FILE, sheet_name='XpressfeedDocs', index=False)
    logger.info('Saved concatenated DataFrame to {}.'.format(settings.DATA_FILE))
    link_list.append(item)
    name_list.append(file_name)
    df_new = pd.DataFrame({'link': link_list,
                           'file_name': name_list
                           })
    concat = pd.concat([df, df_new], ignore_index=True)
    concat.to_excel(settings.DATA_FILE, sheet_name='XpressfeedDocs', index=False)

# load_data_file()
# site_scanner()