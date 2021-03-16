ranges ={
  'temp':{'min':1,'max':45,'Tol_percent':5},#Temperature in Celesius
  'soc':{'min':20,'max':80,'Tol_percent':5},#state of Charge
  'charge_rate':{'min':0,'max':0.8,'Tol_percent':5},#state of Charge
  }
Low_Message ={
                'En':{
                      'temp':"Warning: Approaching low/min Temperature",#Temperature
                      'soc':"Warning: Approaching discharge",#state of Charge
                      'charge_rate':"Warning: Approaching low/min charge rate",#state of Charge
                      },
                'De':{
                  'temp':"Warnung: Annäherung an niedrige / min Temperatur",#Temperature
                  'soc':"Warnung: Annäherung an die Entladung",#state of Charge
                  'charge_rate':"Warnung: Annäherung an eine niedrige Laderate / min",#state of Charge
                      }
}
Mid_Message ={
                'En':{
                      'temp':"Info:The temperature is in the nominal range ",#Temperature
                      'soc':"Info:Battery state Nominal",#state of Charge
                      'charge_rate':"Info: Charge rate Nominal",#state of Charge
                      },
                'De':{
                  'temp':"Info: Die Temperatur liegt im Nennbereich",#Temperature
                  'soc':"Info:Batteriezustand nominal",#state of Charge
                  'charge_rate':"Info: Laderate Nominal",#state of Charge
                      }
}

High_Message ={
            'En':{
              'temp':"Warning: Approaching High/Max Temperature",#Temperature
              'soc':"Warning: Approaching charge-peak",#state of Charge
              'charge_rate':"Warning: Approaching High/Max charge rate",#state of Charge
              },
            'De':{
              'temp':"Warnung: Annäherung an hohe / maximale Temperatur",#Temperature
              'soc':"Warnung: Annäherung an die Ladungsspitze",#state of Charge
              'charge_rate':"Warnung: Annäherung an die hohe / maximale Laderate",#state of Charge
              }
}

test_report=[]
test_case_id=0
selected_Lang='En'#default

def fahrenheit_to_celsisus(temp):
    return ((temp-32)*(5/9))

def kelvin_to_celsisus(temp):
    return (temp-(273.15))

convert_temp_to_celsisus={
    'fah':lambda temp:((temp-32)*(5/9)),#fahrenheit_to_celsisus
    'kel':lambda temp:(temp-(273.15)),#kelvin_to_celsisus
    'cel':lambda temp:temp
    }
def test_input(temp,temp_unit,soc,charge_rate) :
    Dict={'temp':convert_temp_to_celsisus[temp_unit](temp),
          'soc':soc,
          'charge_rate':charge_rate
        }
    return Dict

def append_list(src_list,dst_list):
    for x in src_list:
      dst_list.append(x)
      
    
def get_tolerance_value(attribute):
    return ((attribute['max']*attribute['Tol_percent'])/100)

def info_mid_range_check(attribute_name,attribute_value,attribute_range_min,attribute_range_max,tolerance_value):
    if ((attribute_range_min+tolerance_value)<attribute_value) and (attribute_value<(attribute_range_max-tolerance_value)):
        print(Mid_Message[selected_Lang][attribute_name])
        print(str(attribute_range_min+tolerance_value)+"[Min("+str(attribute_range_min)+")+ Tolerance("+str(tolerance_value)+" )] to "+str(attribute_range_max-tolerance_value)+"[Max("+str(attribute_range_max)+")- Tolerance("+str(tolerance_value)+")]->In °C\n")
     
    
def warn_lower_range_check(attribute_name,attribute_value,attribute_range_min,tolerance_value):
    if (attribute_range_min<attribute_value) and (attribute_value<(attribute_range_min+tolerance_value)):
        print(Low_Message[selected_Lang][attribute_name])
        print(str(attribute_range_min)+"[Min] to "+ str(attribute_range_min+tolerance_value)+"[Min("+str(attribute_range_min)+")+ Tolerance("+str(tolerance_value)+")]->In °C\n")
        
        
def warn_upper_range_check(attribute_name,attribute_value,attribute_range_max,tolerance_value):
    if (attribute_range_max>attribute_value) and (attribute_value>(attribute_range_max-tolerance_value)):
        print(High_Message[selected_Lang][attribute_name])
        print(str(attribute_range_max-tolerance_value)+"[Max("+str(attribute_range_max)+")- Tolerance("+str(tolerance_value)+")] to "+str(attribute_range_max)+"[Max]->In °C\n")
        
        
def early_warnings(attribute_name,attribute_value,attribute_range_min,attribute_range_max):
    tolerance_value=get_tolerance_value(ranges[attribute_name])

    warn_lower_range_check(attribute_name,attribute_value,attribute_range_min,tolerance_value)
    info_mid_range_check(attribute_name,attribute_value,attribute_range_min,attribute_range_max,tolerance_value)
    warn_upper_range_check(attribute_name,attribute_value,attribute_range_max,tolerance_value)
    
def min_range_test(value,range_min):
  result=False #Test step pass->Normal behavior
  test_step='\t\tTeststep::Passed ->Actual value:'+str(value)+' is greater than Min Range:'+str(range_min)
  if value < range_min:
    test_step='\t\tTeststep::Failed ->Actual value:'+str(value)+' is less than Min Range:'+str(range_min)
    result=True #Test step failed->abnormal behavior
  return test_step,result

def max_range_test(value,range_max):
  result=False #Test step pass->Normal behavior
  test_step='\t\tTeststep::Passed ->Actual value:'+str(value)+' is less than Max Range:'+str(range_max)
  if value > range_max:
    test_step='\t\tTeststep::Failed ->Actual value:'+str(value)+' is greater than Max Range:'+str(range_max)
    result=True #Test step failed->abnormal behavior
  return test_step,result

def collect_abnormals(abnormals,test_case_report,attribute_name,attribute_value,attribute_range):

  result=False #Test attribute is within Min and Max range->Normal behavior
  early_warnings(attribute_name,attribute_value,attribute_range['min'],attribute_range['max'])
  
  test_step_min,min_range_result=min_range_test(attribute_value,attribute_range['min'])#test for min range
  test_step_max,max_range_result=max_range_test(attribute_value,attribute_range['max'])#test for max range
  
  if min_range_result or max_range_result:
    result=True #Test attribute is not within Min and Max range->abnormal behavior
    abnormals.append(attribute_name)
  return [test_step_min,test_step_max],result


def report_abnormals_attribute(attribute_report):
  abnormals=[]
  test_case_report=[]

  for attribute in attribute_report:
    report='\tTest Attribute['+attribute+']::->Passed'#Test attribute is within Min and Max range->Normal behavior
    test_step,result=collect_abnormals(abnormals,test_case_report,attribute,attribute_report[attribute],ranges[attribute])
    if result==True:
      report='\tTest Attribute['+attribute+']::->Failed' #Test attribute is not within Min and Max range->abnormal behavior
    test_case_report.append(report)
    append_list(test_step,test_case_report)
  return test_case_report,abnormals

def test_abnormals_attribute(battery_report):

  global test_case_id
  test_case_id+=1
  test_case='Test Case ID['+str(test_case_id)+"]->Passed"
  test_step,abnormals=report_abnormals_attribute(battery_report)
  if(len(abnormals)!=0):
    test_case='Test Case ID::['+str(test_case_id)+"]->Failed"
  test_report.append(test_case)
  append_list(test_step,test_report)


if __name__ == '__main__':
  test_input_battery_report_1=test_input(25,'cel',50,0.4)
  test_input_battery_report_2=test_input(0,'cel',85,0.9)
  test_input_battery_report_3=test_input(33.98,'fah',20.1,0.01)
  test_input_battery_report_4=test_input(317.15,'kel',79,0.7)
  test_abnormals_attribute(test_input_battery_report_1)
  test_abnormals_attribute(test_input_battery_report_2)
  test_abnormals_attribute(test_input_battery_report_3)
  selected_Lang='De'#German
  test_abnormals_attribute(test_input_battery_report_4)
  
  for line in test_report:
    print(line)
