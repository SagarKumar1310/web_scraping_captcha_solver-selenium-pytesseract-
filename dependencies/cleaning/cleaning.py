import pandas as pd

def cleaning_data(self,data_frame):
        
        data_frame[['Title', 'reference_number', 'tender_id']] = data_frame['Title and Ref.No./Tender ID'].str.extract(r'\[(.*?)\]\s*\[(.*?)\]\s*\[(.*?)\]')
        data_frame.drop(columns=["S.No",'Title'], inplace=True)
        data_frame.drop_duplicates()
        columns = data_frame.columns.tolist()
        reordered_columns = columns[-2:] + columns[:-2]
        data_frame = data_frame[reordered_columns]
    
        return data_frame