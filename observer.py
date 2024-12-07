import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates
import time

def read_files(script_dir):
    # Reading all of the csv's that are available in the directory, and storing them in the dictonary.  
    global data_frames
    data_frames = {}
    for filename in os.listdir(script_dir):
        if filename.endswith('.csv'):
            file_path = os.path.join(script_dir,filename)
            data_frames[filename] = pd.read_csv(file_path)
            print("The files that are read are",filename)
    return data_frames
    
def clean_data(data_frames):
    cleaned_data =  {}
    for filename, df in data_frames.items():
        df = df.iloc[60:]
        df = df.iloc[:-60]
        print(filename)
        columns_to_keep=['timestamp','Rate','MB/sec','Resp','Interval','MB_read','MB_write']
        df['timestamp'] = pd.to_datetime(df['timestamp'].str.replace('-BST','').str.replace('-UTC','').str.replace('-GMT',''))
        df['Interval'] = pd.to_numeric(df['Interval'],errors='coerce')
        df = df.loc[:,columns_to_keep]  
        df.set_index('timestamp',inplace=True)
        df_resampled = df.resample('10s').mean().interpolate()
        cleaned_data[filename] = df_resampled.reset_index()
    return cleaned_data


def average_data(cleaned_data):
    average_data = {}
    columns_to_average =['Rate','MB/sec','Resp']
    for filename, df in cleaned_data.items():
        for column in columns_to_average:
            average_value = df[column].mean().round(2)
            df[f'Average_{column}'] = average_value

            average_data[filename] = df
    return average_data
    

def quantiles(average_data):
    quantiled_data = {}
    for filename, df in average_data.items():
        percentiles = df['Rate'].quantile([0.50,0.95,0.98])
        df[f"{filename[:-4]}",'Rate_50th'] = percentiles[0.50]
        df[f"{filename[:-4]}",'Rate_95th'] = percentiles[0.95]
        df[f"{filename[:-4]}",'Rate_98th'] = percentiles[0.98]
        percentiles = df['Resp'].quantile([0.50,0.95,0.98])
        df[f"{filename[:-4]}",'Resp_50th'] = percentiles[0.50]
        df[f"{filename[:-4]}",'Resp_95th'] = percentiles[0.95]
        df[f"{filename[:-4]}",'Resp_98th'] = percentiles[0.98]
        percentiles = df['MB/sec'].quantile([0.50,0.95,0.98])
        df[f"{filename[:-4]}",'MB_sec_50th'] = percentiles[0.50]
        df[f"{filename[:-4]}",'MB_sec_95th'] = percentiles[0.95]
        df[f"{filename[:-4]}",'MB_sec_98th'] = percentiles[0.98]

        


        quantiled_data[filename] = df
    return quantiled_data


def display_table(quantiles_data):
    summary_data = []

    for filename, df in quantiles_data.items():
        avg_rate = df['Average_Rate'].iloc[[0]]
        avg_resp = df['Average_Resp'].iloc[[0]]
        avg_mb_sec = df['Average_MB/sec'].iloc[[0]]
        a = df[f"{filename[:-4]}",'Rate_50th'].iloc[[0]]
        b = df[f"{filename[:-4]}",'Rate_95th'].iloc[[0]]
        c = df[f"{filename[:-4]}",'Rate_98th'].iloc[[0]]
        d = df[f"{filename[:-4]}",'Resp_50th'].iloc[[0]]
        e = df[f"{filename[:-4]}",'Resp_95th'].iloc[[0]]
        f = df[f"{filename[:-4]}",'Resp_98th'].iloc[[0]]
        g = df[f"{filename[:-4]}",'MB_sec_50th'].iloc[[0]]
        h = df[f"{filename[:-4]}",'MB_sec_95th'].iloc[[0]]
        i = df[f"{filename[:-4]}",'MB_sec_98th'].iloc[[0]]
        
        summary_data.append({
            'workload_type': filename[:-4],
            'Average_rate': avg_rate,
            'Average_resp': avg_resp,
            'Average_MB/sec': avg_mb_sec,
            'Rate_92th': a,
            'Rate_95th':b,
            'Rate_98th':c,
            'Resp_92th':d,
            'Resp_95th':e,
            'Resp_98th':f,
            'MB_sec_50th':g,
            'MB_sec_95th':h,
            'MB_sec_98th':i

        })
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_numpy()
        summary_df.to_csv("C:\\Users\\G01232793\\project\\python_scripts\\output\\summary.csv", index=False)
        # print(f"Summary table saved to {save_path}")



def display_data(cleaned_data):
    for filename in clean_data.items():
        print(filename)

# def resample_data(average_data):
#     resample_data = []
#     for filename, df in average_data.items():
#         df.set_index('timestamp',inplace=True)
#         df = df.resample('1T').mean()
#         df.reset_index('timestamp',inplace=True)
#         resample_data[filename] = df
#     return resample_data


def plot_IOPS(df,filename):
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir,'IOPS/')
    os.makedirs(results_dir,exist_ok=True)
    try:
        plt.figure(figsize=(20,8))
        plt.plot(df['Interval'],df['Rate'], marker=',', linestyle='-', color='blue', label='IOPS', alpha=0.7)
        plt.plot(df['Interval'],df['Average_Rate'],linestyle='--',color='red',label='Average IOPS',alpha=0.8)
        plt.title(f"{filename[:-4]}"'- IOPS')
        plt.xlabel('Interval')
        plt.ylabel('IOPS')
        plt.grid()
        plt.text(0.3,0.8,f'Average Rate:{df["Rate"].mean():.2f}',transform=plt.gca().transAxes,ha='center',va='top',fontweight='bold',color='red')
        plt.legend()
        # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        # plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(plt.gca().xaxis.get_majorticklabels(),rotation=45,ha='right')
        plt.savefig(os.path.join(results_dir,f"{filename[:-4]}_IOPS.png"),format='png',dpi=300)
        plt.close()
        print(f"saved a graph for IOPS {filename}")
    except Exception as e:
        print(f"Error plotting for IOPS{filename}:{str(e)}")

def plot_Throughput(df,filename):
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir,'Throughput/')
    os.makedirs(results_dir,exist_ok=True)
    try:
        plt.figure(figsize=(20,8))
        plt.plot(df['Interval'],df['MB/sec'], marker=',', linestyle='-', color='blue', label='Throughput', alpha=0.7)
        plt.plot(df['Interval'],df['Average_MB/sec'],linestyle='--',color='red',label='Average of Average throughput',alpha=0.8)
        plt.title(f"{filename[:-4]}"'- Throughput')
        plt.xlabel('Interval')
        plt.ylabel('Throughput (MB/sec)')
        plt.grid()
        plt.text(0.3,0.8,f'Average MB/sec:{df["MB/sec"].mean():.2f}',transform=plt.gca().transAxes,ha='center',va='top',fontweight='bold',color='red')
        plt.legend()
        # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        # plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(plt.gca().xaxis.get_majorticklabels(),rotation=45,ha='right')
        plt.savefig(os.path.join(results_dir,f"{filename[:-4]}_Throughput.png"),format='png',dpi=300)
        plt.close()
        print(f"saved a graph for MB/sec {filename}")
    except Exception as e:
        print(f"Error plotting for MB/sec{filename}:{str(e)}")

def plot_latency(df,filename):
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir,'Latency/')
    os.makedirs(results_dir,exist_ok=True)
    try:
        plt.figure(figsize=(20,8))
        plt.plot(df['Interval'],df['Resp'], marker=',', linestyle='-', color='blue', label='Latency', alpha=0.7)
        plt.plot(df['Interval'],df['Average_Resp'],linestyle='--',color='red',label='Average Latancy',alpha=0.8)
        plt.title(f"{filename[:-4]}"'-latency')
        plt.xlabel('Interval')
        plt.ylabel('Latency(ms)')
        plt.grid()
        plt.text(0.3,0.8,f'Average Rate:{df["Resp"].mean():.2f}',transform=plt.gca().transAxes,ha='center',va='top',fontweight='bold',color='red')
        plt.legend()
        # plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        # plt.gca().xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(plt.gca().xaxis.get_majorticklabels(),rotation=45,ha='right')
        plt.savefig(os.path.join(results_dir,f"{filename[:-4]}_Latency.png"),format='png',dpi=300)
        plt.close()
        # print("This is the location where it's saved", os.getcwd())
        print(f"saved a graph for Latency {filename}")
    except Exception as e:
        print(f"Error plotting for Latency -  {filename}:{str(e)}")

def plotting_two_values_MB_read_MB_write(df,filename):
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir,'Throughput_RW/')
    os.makedirs(results_dir,exist_ok=True)
    try:
        fig, ax1 = plt.subplots(figsize=(20,8))

        ax1.set_xlabel('Time')
        ax1.set_ylabel('MB_read',color='blue')
        ax1.plot(df['timestamp'],df['MB_read'],color='blue',label='Throughput(MB_read)')
        ax1.tick_params(axis='y',labelcolor='blue')


        ax2 = ax1.twinx()
        ax2.set_ylabel('MB_write',color='red')
        ax2.plot(df['timestamp'],df['MB_write'],color='red',label='Throughput(MB_write)',linestyle='-')
        ax2.tick_params(axis='y',labelcolor='red')
        plt.title(f"{filename[:-4]}"'Throughput(Read/Write)')
        plt.setp(ax1.xaxis.get_majorticklabels(),rotation=45,ha='right')
        fig.legend()
        plt.grid()
        fig.savefig(os.path.join(results_dir,f"{filename[:-4]}_Throughput_RW.png"),format='png',dpi=300)
        fig.tight_layout()
        plt.close()
        print(f"saved a graph for Throughput(Read/Write) - {filename}")
    except Exception as e:
        print(f"Error plotting for Throughput(Read/Write) -  {filename}:{str(e)}")

def plotting_two_values_Throughput_Latency(df,filename):
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir,'Latency_MB/')
    os.makedirs(results_dir,exist_ok=True)
    
    fig, ax1 = plt.subplots(figsize=(20,8))

    ax1.set_xlabel('Time')
    ax1.set_ylabel('MB/sec',color='blue')
    ax1.plot(df['timestamp'],df['MB/sec'],color='blue',label='Throughput(MB/sec)')
    ax1.tick_params(axis='y',labelcolor='blue')


    ax2 = ax1.twinx()
    ax2.set_ylabel('Latency(ms)',color='red')
    ax2.plot(df['timestamp'],df['Resp'],color='red',label='Latency',linestyle='-')
    ax2.tick_params(axis='y',labelcolor='red')
    plt.title(f"{filename[:-4]}"'-Throughput/Latency')
    # ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
    # ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(ax1.xaxis.get_majorticklabels(),rotation=45,ha='right')
    fig.legend()
    plt.grid()
    fig.savefig(os.path.join(results_dir,f"{filename[:-4]}_Throughput_Latency.png"),format='png',dpi=300)
    fig.tight_layout()
    plt.close()

def plotting_two_values_IOPS_Latency(df,filename):
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir,'Latency_IOPS/')
    os.makedirs(results_dir,exist_ok=True)
    fig, ax1 = plt.subplots(figsize=(20,8))


    ax1.set_xlabel('Time')
    ax1.set_ylabel('IOPS',color='blue')
    ax1.plot(df['timestamp'],df['Rate'],color='blue',label='IOPS',linestyle='-')
    ax1.tick_params(axis='y',labelcolor='blue')
 
  
    ax2 = ax1.twinx()
    ax2.set_ylabel('Latency(ms)',color='red')
    ax2.plot(df['timestamp'],df['Resp'],color='red',label='Latency',linestyle='-')
    ax2.tick_params(axis='y',labelcolor='red')
    plt.title(f"{filename[:-4]}"'-IOPS_Latency')
    # ax1.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
    # ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(ax1.xaxis.get_majorticklabels(),rotation=45,ha='right')
    fig.legend()
    plt.grid()
    fig.savefig(os.path.join(results_dir,f"{filename[:-4]}_IOPS_Latency.png"),format='png',dpi=300)
    fig.tight_layout()
    plt.close()

def plot_all_IOPS(average_data):
    n_files = len(average_data)
    colors = plt.cm.brg(np.linspace(0,1,n_files))
    fig, ax1 = plt.subplots(figsize=(20,8))
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir,'plot_all_IOPS/')
    os.makedirs(results_dir,exist_ok=True)
    ax1.set_xlabel('Rate')
    ax1.set_ylabel('IOPS',color='black')
    for (i,(filename,df)) in enumerate (average_data.items()):
        ax1.plot(df['Interval'],df['Rate'],label=f'{filename[:-4]}',color=colors[i])
        ax1.tick_params(axis='y',labelcolor='black')
        ax1.grid(True)
        ax1.legend(loc='center left',bbox_to_anchor=(1,0.5))
        fig.suptitle('IOPS')
    fig.savefig(os.path.join(results_dir,time.strftime("%Y-%m-%d-%H-%M-%S")+"_all_rate.png"),format='png',dpi=300,bbox_inches='tight')

def plot_all_Throughput(average_data):
    n_files = len(average_data)
    colors = plt.cm.brg(np.linspace(0,1,n_files))
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir,'plot_all_Throughput/')
    os.makedirs(results_dir,exist_ok=True)
    fig, ax1 = plt.subplots(figsize=(20,8))
    ax1.set_xlabel('Interval')
    ax1.set_ylabel('Throughput (MB/sec)',color='black')
    for (i,(filename,df)) in enumerate (average_data.items()):
        ax1.plot(df['Interval'],df['MB/sec'],label=f'{filename[:-4]}',color=colors[i])
        ax1.tick_params(axis='y',labelcolor='black')
        ax1.grid(True)
        ax1.legend(loc='center left',bbox_to_anchor=(1,0.5))
        fig.suptitle('MBsec')
    fig.savefig(os.path.join(results_dir,time.strftime("%Y-%m-%d-%H-%M-%S")+'_Throughput.png'),format='png',dpi=300,bbox_inches='tight')

def plot_all_Latency(average_data):
    n_files = len(average_data)
    colors = plt.cm.brg(np.linspace(0,1,n_files))
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir,'plot_all_Latency/')
    os.makedirs(results_dir,exist_ok=True)
    fig, ax1 = plt.subplots(figsize=(20,8))
    ax1.set_xlabel('Interval')
    ax1.set_ylabel('Latency',color='black')
  
    for (i,(filename,df)) in enumerate (average_data.items()):
        ax1.plot(df['Interval'],df['Resp'],label=f'{filename[:-4]}',color=colors[i])
        ax1.tick_params(axis='y',labelcolor='black')
        ax1.grid(True)
        ax1.legend(loc='center left',bbox_to_anchor=(1,0.5))
        fig.suptitle('Latency')
    fig.savefig(os.path.join(results_dir,time.strftime("%Y-%m-%d-%H-%M-%S")+'_Latency.png'),format='png',dpi=300,bbox_inches='tight')
        
def plot_all_Throughput2(average_data):
    countOfFiles = len(data_frames)
    n_files = len(average_data)
    colors = plt.cm.brg(np.linspace(0,1,n_files))
    script_dir = os.path.dirname(__file__)
    results_dir = os.path.join(script_dir,'plot_all_Throughput_RW/')
    os.makedirs(results_dir,exist_ok=True)
    try :
        fig, ax1 = plt.subplots(figsize=(20,8))
        ax1.set_xlabel('Interval')
        ax1.set_ylabel('MB_read',color='black')
        for (i,(filename,df)) in enumerate (average_data.items()):
            ax1.plot(df['Interval'],df['MB_read'],label=f'{filename[:-4]}_read',color=colors[i])
            print(f"i {i}: {filename}")
            ax1.plot(df['Interval'],df['MB_write'],label=f'{filename[:-4]}_write',color=colors[i])
            ax1.tick_params(axis='y',labelcolor='black')
            ax1.grid(True)
            ax1.legend(loc='center left',bbox_to_anchor=(1,0.5))           
            # Rich
            fig.suptitle('Throughput2')
        fig.savefig(os.path.join(results_dir,time.strftime("%Y-%m-%d-%H-%M-%S")+'_Latency.png'),format='png',dpi=300,bbox_inches='tight')
    except Exception as e:
        print(f"Error plotting for Throughput2(Read/Write) -  {filename}:{str(e)}")
    
def main(): 
    script_dir = os.path.dirname(__file__)
    print('------------ Data --------------')
    data = read_files(script_dir)
    print('------------ Files -------------')
    countOfFiles = len(data_frames)
    print("countOfFiles =", (countOfFiles))
    print('------------ Clean Data --------------')
    clean = clean_data(data)
    print('----------- Average --------------')
    average = average_data(clean)
    print('----------- Plot All IOPS data --------------')
    plot_all_IOPS(average)
    print('----------- Plot All Throughput data --------------')
    plot_all_Throughput(average)
    print('----------- Plotting all Latency data --------------')
    plot_all_Latency(average)
    print('------------ Plotting Throughput2 Read/Write --------------')
    plot_all_Throughput2(average)  
  
    for filename, df in average.items():
        plot_IOPS(df,filename)
        print('------------ Plotting single IOPS --------------')
        plot_latency(df,filename)
        print('------------ Plotting single Latency --------------')
        plot_Throughput(df,filename)
        print('------------ Plotting single Throughput --------------')
        plotting_two_values_Throughput_Latency(df,filename)
        print('------------ Plotting two values Latency/Throughput --------------')
        plotting_two_values_IOPS_Latency(df,filename)
        print('------------ Plotting two values IOPS/Latency --------------')
        plotting_two_values_MB_read_MB_write(df,filename)
        print('------------ Plotting Throughput Read/Write --------------')
        
if __name__ =="__main__":
    main() 