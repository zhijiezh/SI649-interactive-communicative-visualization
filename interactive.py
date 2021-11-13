# Zhijie Zhao
# si649f21 Interactive Project

# imports we will use
import pandas as pd
import altair as alt
import streamlit as st
from vega_datasets import data as vega_data
import time
time_start=time.time()
#Title
st.title("Red Lake County is not perfect but definitely not the worst")

#Import data
alt.themes.enable('vox')
counties = alt.topo_feature(vega_data.us_10m.url, 'counties')
geoData = pd.read_pickle('./data_src/geo.pkl')
allinOneData = pd.read_pickle('./data_src/one.pkl')
newEmployData = pd.read_pickle('./data_src/employ.pkl')
redLakeGeoData = geoData[geoData['FIPS_Code'] == 27125]
variableList = ['Natural Amenity Scale', 'Fraction of People who has a College Degree', 'Mean Household Income','Share of Individuals below Poverty Line','Total Crime Rate','High School Dropout Rate','Test Score Percentile']

def vis1Render1(vis1_selectedoption):
  geoBase = alt.Chart(counties).mark_geoshape().encode(
      color=alt.Color(vis1_selectedoption+":Q", scale=alt.Scale(scheme='lighttealblue'),legend=alt.Legend(format=".0%")),
      tooltip=['Natural amenity Scale:N','County name:N']
  ).transform_lookup(
      lookup='id',
      from_=alt.LookupData(geoData, 'FIPS_Code', ['Natural amenity Scale','County name','Land Surface Form Topography Ranking',"Mean Temperature for January Ranking","Mean hours of Sunlight January Ranking","Mean Temperature for July Ranking","Mean relative Humidity July Ranking","Percent Water Area Ranking","Natural amenity Scale Ranking"])
  ).project(
      type='albersUsa'
  ).properties(
      width=500,
      height=300
  ).configure_legend(
  titleFontSize=10,
  labelFontSize=15
  )
  return geoBase 

def vis1Render2(vis_selectedoption):
  naturalBar = alt.Chart(redLakeGeoData).transform_fold(
      ["Land Surface Form Topography Ranking","Mean Temperature for January Ranking","Mean hours of Sunlight January Ranking","Mean Temperature for July Ranking","Mean relative Humidity July Ranking","Percent Water Area Ranking"]
  ).mark_bar().encode(
      alt.X('value:Q', title = None, axis=alt.Axis(format='%')),
      alt.Y('key:N', title = None),
      tooltip=[alt.Tooltip('value:Q',format='.2%')],
      color = alt.Color('value:Q', title = 'Ranking (percentage)',scale=alt.Scale(scheme='lighttealblue'), legend=alt.Legend(format=".0%"))
  )

  naturalBarHighlight = naturalBar.transform_filter(
    alt.datum.key==vis1_selectedoption
  ).mark_bar().encode(
      alt.X('value:Q', title = None, axis=alt.Axis(format='%')),
      alt.Y('key:N', title = None),
      tooltip=[alt.Tooltip('value:Q',format='.2%')],
      color = alt.value('red')
  )

  naturalBar = (naturalBar + naturalBarHighlight).configure_axis(labelLimit=300).resolve_scale(color='independent')
  return naturalBar

def vis2Render(vis2varaible, i):
  legend1 = alt.Chart(allinOneData).mark_bar().encode(
      alt.X('Urban Influence Code 1993:O'),
      alt.Y('average('+ vis2varaible[i][0]+'):Q'),
      tooltip = ['average('+ vis2varaible[i][0]+')'],
      color=alt.value("lightgray")
  )

  selectedAllinOneData = allinOneData[allinOneData["Urban Influence Code 1993"].isin(vis2multiselect)]

  legend1Empasize = alt.Chart(selectedAllinOneData).mark_bar().encode(
      alt.X('Urban Influence Code 1993:O'),
      alt.Y('average('+vis2varaible[i][0]+'):Q'),
      color=alt.Color('Urban Influence Code 1993:O', scale=alt.Scale(scheme='lighttealblue'))
  )

  legend2 = alt.Chart(allinOneData).mark_bar().encode(
      alt.X('Urban Influence Code 1993:O'),
      alt.Y('average('+vis2varaible[i][1]+'):Q'),
      color=alt.value("lightgray")
  )

  legend2Empasize = alt.Chart(selectedAllinOneData).mark_bar().encode(
      alt.X('Urban Influence Code 1993:O'),
      alt.Y('average('+vis2varaible[i][1]+'):Q'),
      tooltip = ['average('+ vis2varaible[i][1]+')'],
      color=alt.Color('Urban Influence Code 1993:O', scale=alt.Scale(scheme='lighttealblue'))
  )
  
  allCollegeIncomeCircle = alt.Chart(selectedAllinOneData).mark_circle().encode(
      alt.X(vis2varaible[i][0]+':Q'),
      alt.Y(vis2varaible[i][1]+':Q'),
      tooltip = ['County name',alt.Tooltip(vis2varaible[i][0],format='.2'),alt.Tooltip(vis2varaible[i][1],format='.2')],
      color=alt.Color('Urban Influence Code 1993:O', scale=alt.Scale(scheme='lighttealblue')),
  )


  redCountyData = selectedAllinOneData[selectedAllinOneData['FIPS_Code']==27125]
  emphasizeCollegeIncomeCircle = alt.Chart(redCountyData).mark_circle(color='red').encode(
          alt.X(vis2varaible[i][0]+':Q', title =vis2varaible[i][0]),
          alt.Y(vis2varaible[i][1]+':Q', title =vis2varaible[i][1]),
      )
  redCountyDataStatic = allinOneData[allinOneData['FIPS_Code']==27125]

  line1 = alt.Chart(redCountyDataStatic).mark_rule(size=2.5).encode(
  y = alt.Y("average("+vis2varaible[i][0]+"):Q"),
  color = alt.value("red")
  )
  line2 = alt.Chart(redCountyDataStatic).mark_rule(size=2.5).encode(
  y = alt.Y("average("+vis2varaible[i][1]+"):Q"),
  color = alt.value("red")
  )
  vis2 =  ((allCollegeIncomeCircle+emphasizeCollegeIncomeCircle).interactive()) & ((legend1+legend1Empasize+line1)|(legend2+legend2Empasize+line2))
  return vis2

def vis3Render():
  selection=alt.selection_interval(bind="scales",encodings=["x"])
  #vertical line
  selection_mouseover_v2 = alt.selection_single(
    on="mouseover", empty="none", fields=['Year']
  )
  condition_opacity_v2 = alt.condition(selection_mouseover_v2, alt.value(1), alt.value(0.0001))

  vLine = alt.Chart(newEmployData).mark_rule(color="lightgray",size=4).add_selection(
    selection_mouseover_v2
  ).encode(
    x="Year:O",
    opacity=condition_opacity_v2
  )
  #interaction dots

  
  dot = alt.Chart(newEmployData).mark_circle(color="black",size=70,tooltip=True).encode(
    x = alt.X("Year:O", title = None),
    y = alt.Y("Unemployment Rate:Q"),
    tooltip = [alt.Tooltip("Unemployment Rate:Q",format='.2'),"Year:O",],
    opacity=condition_opacity_v2
  ).add_selection(selection)
  employPlot = alt.Chart(newEmployData).mark_line().encode(
      x='Year:O',
      y= alt.Y('Unemployment Rate:Q', title = 'Unemployment Rate (%)'),
      color = alt.condition(alt.datum['County Name/State Abbreviation']=='Red Lake County, MN',alt.value('red'),alt.Color('County Name/State Abbreviation:N',legend=alt.Legend(values = ['Average','Rural Average']),scale=alt.Scale(scheme='lighttealblue')))
  )
  vis3 = (employPlot+vLine+dot)
  return vis3

def vis4Render():
  selection=alt.selection_interval()
  # selection2=alt.selection_single(on="mouseover");
  opacityCondition = alt.condition(selection,alt.value(0.5),alt.value(0.01))

  

  # slider_hhinc
  hhinc_min = allinOneData['Mean Household Income'].min()
  hhinc_max = allinOneData['Mean Household Income'].max()

  hhinc_slider_max = alt.binding_range(
    min=hhinc_min,
    max=hhinc_max,
    step=1,
    name="Mean Household Income Max"
  )

  hhinc_slider_min = alt.binding_range(
    min=hhinc_min,
    max=hhinc_max,
    step=1,
    name="Mean Household Income Min"
  )

  hhinc_selector_max = alt.selection_single(
    bind = hhinc_slider_max,
    fields = ["hhinc_max"],
    init = {"hhinc_max":hhinc_max}
  )

  hhinc_selector_min = alt.selection_single(
    bind = hhinc_slider_min,
    fields = ["hhinc_min"],
    init = {"hhinc_min":hhinc_min}
  )

    # slider_frac_coll
  frac_coll_min = allinOneData['Fraction of People who has a College Degree'].min()
  frac_coll_max = allinOneData['Fraction of People who has a College Degree'].max()

  frac_coll_slider_max = alt.binding_range(
    min=frac_coll_min,
    max=frac_coll_max,
    step=0.001,
    name="Fraction of People who has a College Degree Max"
  )

  frac_coll_slider_min = alt.binding_range(
    min=frac_coll_min,
    max=frac_coll_max,
    step=0.001,
    name="Fraction of People who has a College Degree Min"
  )

  frac_coll_selector_max = alt.selection_single(
    bind = frac_coll_slider_max,
    fields = ["frac_coll_max"],
    init = {"frac_coll_max":frac_coll_max} 
  )

  frac_coll_selector_min = alt.selection_single(
    bind = frac_coll_slider_min,
    fields = ["frac_coll_min"],
    init = {"frac_coll_min":frac_coll_min}
  )

  # slider_poor_share
  poor_share_min = allinOneData['Share of Individuals below Poverty Line'].min()
  poor_share_max = allinOneData['Share of Individuals below Poverty Line'].max()

  poor_share_slider_max = alt.binding_range(
    min=poor_share_min,
    max=poor_share_max,
    step=0.001,
    name="Share of Individuals below Poverty Line Max"
  )

  poor_share_slider_min = alt.binding_range(
    min=poor_share_min,
    max=poor_share_max,
    step=0.001,
    name="Share of Individuals below Poverty Line Min"
  )

  poor_share_selector_max = alt.selection_single(
    bind = poor_share_slider_max,
    fields = ["poor_share_max"],
    init = {"poor_share_max":poor_share_max} 
  )

  poor_share_selector_min = alt.selection_single(
    bind = poor_share_slider_min,
    fields = ["poor_share_min"],
    init = {"poor_share_min":poor_share_min}
  )

  # slider_crime_total
  crime_total_min = allinOneData['Total Crime Rate'].min()
  crime_total_max = allinOneData['Total Crime Rate'].max()

  crime_total_slider_max = alt.binding_range(
    min=crime_total_min,
    max=crime_total_max,
    step=0.001,
    name="Total Crime Rate Max"
  )

  crime_total_slider_min = alt.binding_range(
    min=crime_total_min,
    max=crime_total_max,
    step=0.001,
    name="Total Crime Rate Min"
  )

  crime_total_selector_max = alt.selection_single(
    bind = crime_total_slider_max,
    fields = ["crime_total_max"],
    init = {"crime_total_max":crime_total_max} 
  )

  crime_total_selector_min = alt.selection_single(
    bind = crime_total_slider_min,
    fields = ["crime_total_min"],
    init = {"crime_total_min":crime_total_min}
  )

  # slider_dropout_r
  dropout_r_min = allinOneData['High School Dropout Rate'].min()
  dropout_r_max = allinOneData['High School Dropout Rate'].max()

  dropout_r_slider_max = alt.binding_range(
    min=dropout_r_min,
    max=dropout_r_max,
    step=0.001,
    name="High School Dropout Rate Max"
  )

  dropout_r_slider_min = alt.binding_range(
    min=dropout_r_min,
    max=dropout_r_max,
    step=0.001,
    name="High School Dropout Rate Min"
  )

  dropout_r_selector_max = alt.selection_single(
    bind = dropout_r_slider_max,
    fields = ["dropout_r_max"],
    init = {"dropout_r_max":dropout_r_max} 
  )

  dropout_r_selector_min = alt.selection_single(
    bind = dropout_r_slider_min,
    fields = ["dropout_r_min"],
    init = {"dropout_r_min":dropout_r_min}
  )

  # slider_score_r
  score_r_min = allinOneData['Test Score Percentile'].min()
  score_r_max = allinOneData['Test Score Percentile'].max()

  score_r_slider_max = alt.binding_range(
    min=score_r_min,
    max=score_r_max,
    step=0.1,
    name="Test Score Percentile Max"
  )

  score_r_slider_min = alt.binding_range(
    min=score_r_min,
    max=score_r_max,
    step=0.1,
    name="Test Score Percentile Min"
  )

  score_r_selector_max = alt.selection_single(
    bind = score_r_slider_max,
    fields = ["score_r_max"],
    init = {"score_r_max":score_r_max} 
  )

  score_r_selector_min = alt.selection_single(
    bind = score_r_slider_min,
    fields = ["score_r_min"],
    init = {"score_r_min":score_r_min}
  )

  # slider_natural
  natural_min = allinOneData['Natural Amenity Scale'].min()
  natural_max = allinOneData['Natural Amenity Scale'].max()

  natural_slider_max = alt.binding_range(
    min=natural_min,
    max=natural_max,
    step=0.01,
    name="Natural Amenity Scale Max"
  )

  natural_slider_min = alt.binding_range(
    min=natural_min,
    max=natural_max,
    step=0.01,
    name="Natural Amenity Scale Min"
  )

  natural_selector_max = alt.selection_single(
    bind = natural_slider_max,
    fields = ["natural_max"],
    init = {"natural_max":natural_max} 
  )

  natural_selector_min = alt.selection_single(
    bind = natural_slider_min,
    fields = ["natural_min"],
    init = {"natural_min":natural_min}
  )


  # selfmade selector
  makeselection = alt.selection_multi(fields=['key'])
  color = alt.condition(makeselection, alt.Color('key:N', scale=alt.Scale(scheme='accent'), legend= None), alt.value('lightgray'))
  make = pd.DataFrame({'key':variableList})
  selmadeSelector = alt.Chart(make).mark_rect().encode(
     y= alt.Y('key:N',sort=variableList,title=None),
    color=color
    ).add_selection(
      makeselection,
      selection,
      score_r_selector_max,
      score_r_selector_min,
      dropout_r_selector_max,
      dropout_r_selector_min,
      crime_total_selector_max,
      crime_total_selector_min,
      poor_share_selector_max,
      poor_share_selector_min,
      hhinc_selector_max,
      hhinc_selector_min,
      frac_coll_selector_max,
      frac_coll_selector_min,
      natural_selector_max,
      natural_selector_min
  )

  test1 = alt.Chart(allinOneData).transform_window(
      index='count()'
  ).transform_fold(
     variableList
  ).transform_joinaggregate(
      min='min(value)',
      max='max(value)',
      groupby=['key']
  ).transform_calculate(
      minmax_value=(alt.datum.value-alt.datum.min)/(alt.datum.max-alt.datum.min),
      mid=(alt.datum.min+alt.datum.max)/2
  ).mark_line().transform_filter(
    alt.datum['Mean Household Income'] < hhinc_selector_max.hhinc_max
  ).transform_filter(
    alt.datum['Mean Household Income'] > hhinc_selector_min.hhinc_min
  ).transform_filter(
    alt.datum['Fraction of People who has a College Degree'] < frac_coll_selector_max.frac_coll_max
  ).transform_filter(
    alt.datum['Fraction of People who has a College Degree'] > frac_coll_selector_min.frac_coll_min
  ).transform_filter(
    alt.datum['Share of Individuals below Poverty Line'] < poor_share_selector_max.poor_share_max
  ).transform_filter(
    alt.datum['Share of Individuals below Poverty Line'] > poor_share_selector_min.poor_share_min
  ).transform_filter(
    alt.datum['Total Crime Rate'] < crime_total_selector_max.crime_total_max
  ).transform_filter(
    alt.datum['Total Crime Rate'] > crime_total_selector_min.crime_total_min
  ).transform_filter(
    alt.datum['High School Dropout Rate'] < dropout_r_selector_max.dropout_r_max
  ).transform_filter(
    alt.datum['High School Dropout Rate'] > dropout_r_selector_min.dropout_r_min
  ).transform_filter(
    alt.datum['Test Score Percentile'] < score_r_selector_max.score_r_max
  ).transform_filter(
    alt.datum['Test Score Percentile'] > score_r_selector_min.score_r_min
  ).transform_filter(
    alt.datum['Natural Amenity Scale'] < natural_selector_max.natural_max
  ).transform_filter(
    alt.datum['Natural Amenity Scale'] > natural_selector_min.natural_min
  ).transform_filter(makeselection).encode(
      y= alt.Y('key:N',sort=variableList,title=None),
      x= alt.X('minmax_value:Q', title="Normalized Scale", scale=alt.Scale(domain=[0, 1])),
      color= "Urban Influence Code 1993:N",
      detail='index:N',
      opacity=opacityCondition,
      tooltip=['County name']
  ).properties(width=500,height=800)

  # deploy vis4
  vis4 = (test1 | selmadeSelector).resolve_scale(color='independent').configure_axis(labelLimit=300)
  return vis4





def returnHelper(num):
  for _ in range(num):
    st.sidebar.write(' ')

#Sidebar
dropdown_list = ["Natural Amenities Scale", "Education and Economy", "Improvement in unemployment", "Patterns hidden inside"]
vis_select = st.sidebar.selectbox(label="Select a visualization to display", options=dropdown_list)
pos = 0

time_end = time.time()
print('Import time: ',time_end-time_start)


if vis_select == dropdown_list[0]:
  st.write("## Does Red Lake County have good natural amenities?")
  vis1options = ["Natural amenity Scale Ranking", "Land Surface Form Topography Ranking","Mean Temperature for January Ranking","Mean hours of Sunlight January Ranking","Mean Temperature for July Ranking","Mean relative Humidity July Ranking","Percent Water Area Ranking"]
  vis1_selectedoption = st.selectbox('Choose the one of the six measures of natural amenities scale that your are interested in:', vis1options)
  st.write('*The higher the ranking in percentile is, the worse.*')
  geoBase = vis1Render1(vis1_selectedoption)
  st.altair_chart(geoBase, use_container_width=True)
  st.write("From the map on the right, we can see natural amenities are strongly correlated with the geographical location. Sitting in the interior of the northern U.S. deeply influences this county.")
  st.write("Then we can answer the question. No, the ranking (in percentage) of all six natural amenities are over **50%** and more than 3 of them are larger than **90%**. That’s why Red Lake County is called the “America’s worst place to live”")

  naturalBar = vis1Render2(vis1_selectedoption)
  st.altair_chart(naturalBar, use_container_width=True)
  print('Vis1: ',time.time()-time_end)
  time_end = time.time()

if vis_select == dropdown_list[1]:
  st.write("## Education and Economy")
  vis2varaible= [
    ['Fraction of People who has a College Degree','Mean Household Income'],
    ['Share of Individuals below Poverty Line','Total Crime Rate'],
    ['High School Dropout Rate','Test Score Percentile']
    ]
  vis2variableoptions = [
    "Parts that Red Lake County is not so good at",
    "Parts that Red Lake County is good at (economy)",
    "Parts that Red Lake County is good at (education)"
    
    ]
  vis2Title = [
    '**Is Red Lake County rich and people there all go to college?**',
    '**High rankings in poverty rate and crime rate makes Red Lake County a good place to live in**',
    '**Red Lake County provides decent fundamental education**'
  ]
  vis2content = [
    'Not really. the mean household income of Red Lake County is **54444.098** dollar, which only beats **22%** of counties in the US. Only **13%** of people in Red Lake County aged 25 or older who have a bachelor\'s degree, master\'s degree, professional school degree, or doctorate degree.',
    'Only **10.7%** of people in Red Lake County are below the federal poverty line. The total crime rate of Red Lake County is extremely close to zero, which is **0.00047%**.',
    'Red Lake County has a low high school drop out rate at **-2.65%**, which ranks very high in all counties. Nevertheless, the test score of high school students in Red Lake County is descent. The test score percentile of Red Lake County is **3.89%**',
  ]
  vis2singleselect = st.selectbox('Choose what topic you want to see',vis2variableoptions)
  i = vis2variableoptions.index(vis2singleselect)
  vis2options = list(range(1,10))
  vis2multiselect = st.sidebar.multiselect('Select the urban influence code:',vis2options,vis2options,help="Urban influence code represent a place is urban or rural. 1 means completely urban while 9 means completely rural.")
  vis2 = vis2Render(vis2varaible, i)
  st.write(vis2Title[i])
  st.write("*Urban influence code represent a place is urban or rural. 1 means completely urban while 9 means completely rural.*")
  st.write("*The Urban influence code of Red Lake County is 9.*")
  st.altair_chart(vis2, use_container_width=True)
  st.write(vis2content[i])

  print('Vis2: ',time.time()-time_end)
  time_end = time.time()

if vis_select == dropdown_list[2]:
  st.write('## Red Lake County has done a great job  in decreasing the unemployment rate')
  vis3 = vis3Render()
  st.altair_chart(vis3, use_container_width=True)
  st.write('The unemployment Rate of Red Lake County has dropped from **15.1%** in 1990 to **6%** in 2015, which is a lot faster compared to the average of all counties in the United States as well as the average of other completely rural counties.')

  print('Vis3: ',time.time()-time_end)
  time_end = time.time()

if vis_select == dropdown_list[3]:
  # vis 4
  
  vis4 = vis4Render()
  st.write('## Patterns hidden inside the data')
  st.write('Thanks for reading my visualization. Here is the last step of this little vis project. Try yourselves to find out the pattern hiddens in those variables.')
  st.write('Let me introduce this vis tool to you. This is a parallel coordinate graph, which can be used to find relations between variables, below are the given tools to intract with this graph:')
  st.write('- At the bottom we have multiple sliders, you can use those to filter the lines.')
  st.write('- On the right, the rainbow-colored plot is a multi-selection panel where you can filter on different variables. **Hold shift to choose multiple variables!!!**')
  st.write('You will see the interesting points mentioned above just by sliding the *Natural Amenity Scale Max* to the left. ( i.e. High Test Score Percentile, Low High School Dropout Rate )')
  st.altair_chart(vis4, use_container_width=True)

  print('Vis4: ',time.time()-time_end)
  time_end = time.time()