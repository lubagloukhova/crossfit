setwd("/Users/lubagloukhov/PycharmProjects/scrapely01")

# Load Packages:
  library(ggplot2)
  library(reshape)
  library(RColorBrewer)

# For FiveThirtyEight Theme:
  library(devtools)
  install_github("ggthemes", "jrnold")# for fivethirtyeight theme
  library(ggthemes)

# Load & Prepare Data (Named WODS)
  namedWOD <- read.table('CFnamedWOD.txt', stringsAsFactor=FALSE, sep = "\n")
  namedWOD <- tolower(namedWOD[['V1']])
  namedWOD <- gsub(" ",".", namedWOD) # modify to match mDFday var

# Load & Prepare Data (Monthly Dict)
  DF <- read.csv('movemonthDict.csv', stringsAsFactors=F)
  DF$X <- as.Date(DF$X)

# Load & Prepare Data (Daily Dict)
  DFday <- read.csv('dateDF.csv', stringsAsFactors=F)
  mDFday <- melt(DFday, id=c("X"))
  mDFday <- mDFday[!is.na(mDFday$value),]
  mDFday$value <- (as.Date(mDFday$value))
  mDFday$quarter <- cut (mDFday$value, breaks="quarter")
  mDFday$quarter<-as.Date(mDFday$quarter)
  mDFday$year <- cut (mDFday$value, breaks="year", 
                      labels=seq(2001,2014))

# Find vars that end in .1 & modify them to remove .1
  var2<-as.character(unique(mDFday$variable)[grepl("^.+(1)$",unique(mDFday$variable))])
  for (i in 1:length(var2)){
    mDFday[mDFday$variable==var2[i],"variable"] <- substr(mDFday[mDFday$variable==var2[i,"variable"] , 1, nchar(as.character(mDFday[mDFday$variable==var2[i],"variable"][[1]]) )-2)
  }

# Recreate Python ggplot
  qplot(DF$X, DF$tabata, geom="bar", stat="identity")

# Plot Modifications:
  labels <- seq(2001, 2014, by=4) # X axis labels
  colourCount <- length(unique(topCountSub$variable)) # colors
  getPalette <- colorRampPalette(brewer.pal(9, "Set1"))


# TOP MOVEMENT WOD COUNTS

agg <- aggregate(value ~ variable, mDFday, length)
vars <- as.character(agg[ order(-agg$value)[c(1,2,4:17,19:26)], "variable"])

topCountSub<- mDFday[mDFday$variable %in% (vars),]
topCountSub$variable <- factor(topCountSub$variable, 
                               levels=(vars)) # redefine levels to drop empty

ggplot(topCountSub, aes(year, fill=variable))+ geom_bar() + facet_wrap(~ variable, ncol=4) +
  scale_x_discrete(breaks=labels, labels=as.character(labels)) +
  theme_fivethirtyeight() + 
  theme(axis.title.x = element_text(),axis.title.y = element_text(angle = 90,vjust = 1),
        axis.title = element_text(), legend.position="none",
        text = element_text(size=4))  +
  scale_fill_manual(values=getPalette(colourCount)) +
  xlab("Year") +
  ylab("Number of WODs with Movement") 

ggsave(file="movePlot.jpeg", width=3, height=6)

# TOP NAMED WOD COUNTS

namedWODSub<- mDFday[mDFday$variable %in% namedWOD,]
namedWODSub <- namedWODSub[!is.na(namedWODSub$variable), ]

agg <- aggregate(value ~ variable, namedWODSub, length)
vars <- as.character(agg[ order(-agg$value)[2:22], "variable"])
#first is "crossfit, exclude it!

# subset to include only top 21  by workout count
topNamedCountSub<- namedWODSub[namedWODSub$variable %in% (vars),]
topNamedCountSub$variable <- factor(topNamedCountSub$variable, 
                                    levels=(vars)) # redefine levels to drop empty

ggplot(topNamedCountSub, aes(year, fill=variable)) + geom_bar() + 
  facet_wrap(~ variable, ncol=3) +
  scale_x_discrete(breaks=labels, labels=as.character(labels)) +
  theme_fivethirtyeight() + 
  theme(axis.title.x = element_text(),axis.title.y = element_text(angle = 90,vjust = 1),
        axis.title = element_text(), legend.position="none",
        text = element_text(size=4))  +
  scale_fill_manual(values=getPalette(colourCount)) +
  xlab("Year") +
  ylab("Number of Named WODs") 

ggsave(file="namedPlot.jpeg", width=3, height=6)

# SWIM/BIKE/RUN/ROW WOD COUNTS

rbsrVars <- c("run", "swim", "bike", "row")
rbsrVarsSub<- mDFday[mDFday$variable %in% rbsrVars,]
rbsrVarsSub <- rbsrVarsSub[!is.na(rbsrVarsSub$variable), ]

ggplot(rbsrVarsSub, aes(year, fill=variable))+ geom_bar() + facet_wrap(~ variable, ncol=4) +
  scale_x_discrete(breaks=labels, labels=as.character(labels)) +
  theme_fivethirtyeight() + 
  theme(axis.title.x = element_text(),axis.title.y = element_text(angle = 90,vjust = 1),
        axis.title = element_text(), legend.position="none",
        text = element_text(size=4))  +
  scale_fill_manual(values=getPalette(colourCount)) +
  xlab("Year") +
  ylab("Number of WODs with Movement") 

ggsave(file="rbsrPlot.jpeg", width=3, height=1.5)

