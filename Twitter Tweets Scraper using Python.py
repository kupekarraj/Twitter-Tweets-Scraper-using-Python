#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
import time
from pandas import DataFrame
from datetime import date,datetime,timedelta
from selenium.webdriver.common.by import By


# In[ ]:


def driver_initialize():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--dns-prefetch-disable")
    driver=webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
    driver.set_page_load_timeout(300)
    return driver


# In[ ]:


driver=driver_initialize()


# In[ ]:


def scraper():
    rows=[]
    queries=open('input.txt','r').readlines()
    for query in queries:
        
        query=query.replace('\n','')
        date_from=query.split('since:')[1].strip()
        date_until=query.split('until:')[1].strip().split('since:')[0].strip()
        user=query.split('from:')[1].strip().split(')')[0].replace('@','')
        web_query='https://twitter.com/search?q=(from%3A'+user+')%20until%3A'+date_until+'%20since%3A'+date_from+'&src=typed_query&f=live'
        driver.get(web_query)
        time.sleep(5)
        SCROLL_PAUSE_TIME=0.5
        height=500
        last_height = driver.execute_script("return document.body.scrollHeight")
        count=0
        is_end=False
        while True:
            nodes=driver.find_elements(By.XPATH,'//div[@aria-label="Timeline: Search timeline"]/div/div')
            for node in nodes:
                tweet_url="";tweet_copy='';posttime="";postdate="";likes='';retweets='';quote_tweets='';replies='';photos='No';links='0';videos='No';hashtags=''
                try:
                    tweet_url=node.find_element(By.XPATH,'.//a[@role="link"][@class][@aria-label][contains(@href,"/status/")]').get_attribute('href')
                    print("Tweet URL: "+tweet_url)
                except:
                    continue
                try:
                    tweet_copy=node.find_element(By.XPATH,'.//div[@data-testid="tweetText"]').get_attribute('innerText')
                    print("Tweet Text: "+tweet_copy)
                except:
                    pass
                try:
                    posttime=node.find_element(By.XPATH,'.//a[@role="link"][@class][@aria-label][contains(@href,"/status/")]/time').get_attribute('datetime').split('T')[1]
                    print("Post Time: "+posttime)
                except:
                    pass
                try:
                    postdate=node.find_element(By.XPATH,'.//a[@role="link"][@class][@aria-label][contains(@href,"/status/")]/time').get_attribute('datetime').split('T')[0]
                    print("Post Date: "+postdate)
                except:
                    pass
                try:
                    likes=node.find_element(By.XPATH,'.//div[@data-testid="like"]').get_attribute('aria-label').replace('Likes. Like','').replace('Like. Like','').strip()
                    print("Post Likes: "+likes)
                except:
                    pass
                try:
                    retweets=node.find_element(By.XPATH,'.//div[@data-testid="retweet"]').get_attribute('aria-label').replace('Retweets. Retweet','').replace('Retweet. Retweet','').strip()
                    print("Post Retweets: "+retweets)
                except:
                    pass
                try:
                    replies=node.find_element(By.XPATH,'.//div[@data-testid="reply"]').get_attribute('aria-label').replace('Replies. Reply','').replace('Reply. Reply','').strip()
                    print("Post Replies: "+replies)
                except:
                    pass
                try:
                    node.find_element(By.XPATH,'.//div[@data-testid="videoPlayer"]')
                    videos='Yes'
                    photos='No'
                except:
                    pass
                if videos=='No':
                    try:
                        node.find_element(By.XPATH,'.//div[@data-testid="tweetPhoto"]')
                        photos='Yes'
                        videos='No'
                    except:
                        pass
                links_count=0
                try:
                    links_nodes=node.find_elements(By.XPATH,'.//div[@data-testid="tweetText"]//a')
                    for l_node in links_nodes:
                        try:
                            l_node_url=l_node.get_attribute('href')
                            if 'https://t.co' in l_node_url:
                                links_count+=1
                        except:
                            continue
                except:pass
                links=str(links_count)
                try:
                    hashtag_nodes=node.find_elements(By.XPATH,'.//div[@data-testid="tweetText"]//a[contains(@href,"/hashtag/")]')
                    for h_node in hashtag_nodes:
                        hashtags+=h_node.get_attribute('innerText')+' | '
                except:
                    pass
                try:
                    hashtags=hashtags[:-2]
                except:
                    pass
                row=[tweet_url,tweet_copy,posttime,postdate,likes,retweets,quote_tweets,replies,photos,videos,links,hashtags,query]
                rows.append(row)
            while True:
                try:
                    driver.find_element(By.XPATH,"//div/span/span[text()='Retry']").click()
                    time.sleep(3)
                except:
                    break

            
            driver.execute_script("window.scrollBy(0, "+str(height)+");")
            time.sleep(SCROLL_PAUSE_TIME)
            #new_height = driver.execute_script("return document.body.scrollHeight")
            #if new_height == last_height:
            #    count+=1
            #    driver.execute_script("window.scrollBy(0, "+str(height)+");")
            #    time.sleep(5)
            #else:
            #    last_height = new_height
            #    count=0
            try:
                driver.find_element(By.XPATH,"//div[@data-testid='cellInnerDiv'][last()]/div/div/div")
                count=0
                is_end=False
            except:
                driver.execute_script("window.scrollBy(0, "+str(height)+");")
                time.sleep(SCROLL_PAUSE_TIME)
                is_end=True
                count+=1
                pass
            if count==50 and is_end:
                break
    unique_rows=[]
    for row in rows:
        if row not in unique_rows:
            unique_rows.append(row)        
    df=DataFrame(unique_rows,columns=['Tweet URL','Tweet Copy','Time','Date','Likes','Retweets','Quote Tweets','Replies','Photos','Videos','Links','Hashtags','Query'])
    df.drop_duplicates(inplace=True)
    now=datetime.now()
    date_time=now.strftime('%m-%d-%Y %H-%M-%S')
    df.to_excel('Data Exported On '+str(date_time)+'.xlsx',sheet_name='Sheet1',index=False,encoding='utf-8')  

scraper()  


# In[ ]:


import os
os.getcwd()

