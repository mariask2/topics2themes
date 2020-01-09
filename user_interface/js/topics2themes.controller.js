"use strict";

// Offset size used for the container panel headings
var TOP_OFFSET = 45;

// Stroke widths used for the term-to-topic links
var TERM_TO_TOPIC_LINK_WIDTHS = [1, 3];

var TOPIC_TO_TEXT_LINK_WIDTHS = [0.2, 2];

// Just for consistency in the code. All links equal here
var TEXT_THEME_LINK_WIDTHS = [0.5, 0.5];

// Current window size (used to ignore redundant resize events)
var windowWidth;
var windowHeight;

// Search field values
var termSearchText = "";
var topicSearchText = "";
var textSearchText = "";
var themeSearchText = "";

var DIRECTHIGHLIGHT = "direct-highlight";

var DIRECTCHOOSEN = "direct-chosen";

var CHOOSEN = "indirect-chosen";

var HIGHLIGHT = "highlight";

var NOTCHOSEN = "not-chosen";

var SELECTDATASETTEXT = "Select data set";
var SELECTMODELTEXT = "Select model";
var SELECTANALYSISTEXT = "Select analysis";

var showLabels = true;
var doThemesSorting = true;
var lockTextsSorting = false;
var lockTermsSorting = false;
var lockTopicsSorting = false;

// Holds terms selected, splitted for "/" and "_" into different terms
var splittedTerms = [];

/// Sort functions
/////////////////////

// Sort functions for documents
/*var SORT_DOCUMENTS = {
	"time/asc": compareDocumentTimestampAsc,
	"time/desc": compareDocumentTimestampDesc
};*/

// Sort functions for terms
var SORT_TERMS = {
	"score/desc": sortTermsScoreDesc,
	"score/asc": sortTermsScoreAsc,
	"topics/desc": sortTermsTopicsDesc,
	"topics/asc": sortTermsTopicsAsc,
	"docs/desc": sortTermsDocsDesc,
	"docs/asc": sortTermsDocsAsc,
	"alpha/desc": sortTermsAlphaDesc,
	"alpha/asc": sortTermsAlphaAsc
};

var SORT_TEXT= {
    "score/desc": sortTextScoreDesc,
    "score/asc": sortTextScoreAsc
};

var SORT_TOPIC= {
    "score/desc": sortTopicScoreDesc,
    "score/asc": sortTopicScoreAsc
};

var SORT_THEME= {
    "time/asc": sortThemesTimeAsc,
    "time/desc": sortThemesTimeDesc,
    "texts/asc" : sortThemesNumberofTextsAsc,
    "texts/desc" : sortThemesNumberofTextsDesc
};

// Current sorting modes for each list (based on sorting keys)
var termSortMode = null;
var topicSortMode = null;
var textSortMode = null;
var themeSortMode = null;

var authenticationKey = null;



/////////////////////
// Script entry point
//////////////////////

$(document).ready(function(){
                  
    getAuthenticationKey();
	windowWidth = $(window).width();
	windowHeight = $(window).height();
	
	resizeContainers();
	
    ////////////////////////
	// Set up the handlers
    /////////////////////////
    
    // Handlers for selecting and/or constructing data sets, models and analysis 
    $("#dataset").change(onDatasetChange);
    $("#newModel").click(onConstructNewModel);
    $("#modelVersion").change(onModelVersionListChange);
    $("#newAnalysis").click(onNewAnalysis);
    $("#analysisVersion").change(onAnalysisVersionListChange);    
    $("#exportAnalysis").click(onExportAnalysis);                  

    // Search buttons
    $("#termSearchButton").click(onTermSearchButtonClick);
    $("#topicSearchButton").click(onTopicSearchButtonClick);
    $("#textSearchButton").click(onTextSearchButtonClick);
    $("#themeSearchButton").click(onThemeSearchButtonClick);
                  
                  
	$("#termsList, #topicsList, #themesList, #textsList").scroll(onListScroll);
	
	
	$("#termSearchClear").click(onTermSearchClear);
	$("#termSearch").keyup(onTermSearch);
	$("#topicSearchClear").click(onTopicSearchClear);
	$("#topicSearch").keyup(onTopicSearch);
	$("#textSearchClear").click(onTextSearchClear);
	$("#textSearch").keyup(onTextSearch);
	$("#themeSearchClear").click(onThemeSearchClear);
	$("#themeSearch").keyup(onThemeSearch);
	
	
	$("#topicsList").on("change", ".topic-element .title-label", onTopicRename);
    $("#newTheme").click(onThemeAdd);
	$("#themesList").on("change", ".theme-element .title-label", onThemeRename);
    $("#textsList").on("click", ".text-element .change-label-trigger", onChooseLabelClick);
    $("#textsList").on("click", ".text-element .theme-text-remove-button", onThemeTextRemoveAtTextElement);
	$("#themesList").on("click", ".theme-element .theme-remove-button", onThemeRemove);
	
	$(".sort-terms-trigger").click(onSortTermsList);
	$(".sort-topics-trigger").click(onSortTopicsList);
	$(".sort-documents-trigger").click(onSortDocumentsList);
    $(".sort-themes-trigger").click(onSortThemesList);
                  
	// list click events to select a items as active
    $("#termsList").on("dblclick", ".term-element", onTermElementClick);
    $("#topicsList").on("dblclick", ".topic-element", onTopicElementClick);
    $("#textsList").on("dblclick", ".text-element", onTextElementClick);
    $("#themesList").on("dblclick", ".theme-element", onThemeElementClick);

    $("#textsList").on("mouseup", ".jp_lemma", onSelectionChange);
    
                 
    // Button for hide and show labels on themes
    $("#showLabels").click(onShowLabels);
                  
    // Button for lock and unlock the sorting of themes
    $("#doThemeSorting").click(onLockThemesSorting);

    // Button for lock and unlock the sorting of texts
    $("#lockTextSorting").click(onLockTextSorting);

    // Button for lock and unlock the sorting of terms
    $("#lockTermsSorting").click(onLockTermsSorting);

      // Button for lock and unlock the sorting of terms
    $("#lockTopicsSorting").click(onLockTopicsSorting);

             
    // Drag'n'drop handlers
    	$("#textsList")
	.on("dragstart", ".label-button-container", onTextElementDragStart)
		.on("dragend", ".label-button-container", onTextElementDragEnd);
                  
	$("#themesList")
		.on("dragenter", ".theme-element", onThemeElementDragEnterOver)
		.on("dragover", ".theme-element", onThemeElementDragEnterOver)
		.on("dragleave", ".theme-element", onThemeElementDragLeave)
		.on("drop", ".theme-element", onThemeElementDrop);
	

	// Highlight handlers
    $("#textsList")
		.on("mouseenter", ".text-element", onTextElementMouseEnter)
        .on("mouseleave", ".text-element", onTextElementMouseLeave);
	$("#termsList")
		.on("mouseenter", ".term-element", onTermElementMouseEnter)
		.on("mouseleave", ".term-element", onTermElementMouseLeave);
	$("#topicsList")
		.on("mouseenter", ".topic-element", onTopicElementMouseEnter)
		.on("mouseleave", ".topic-element", onTopicElementMouseLeave);
	$("#themesList")
		.on("mouseenter", ".theme-element", onThemeElementMouseEnter)
		.on("mouseleave", ".theme-element", onThemeElementMouseLeave);
	
	
    disableModelChoices();
    disableAnalysisChoices();
    disableThemeButtons();
    resetInterface();
    modelCurrentDataset = null;
                  
    // Load the dataset choices
    populateDataChoices();
                  
    // Check if the create model button is to be enabled
    modelCanModelBeCreated();
});


function onSelectionChange(){
    let explanation = $(this).attr("exp")
    // TODO: Future version, care about if something is selected. Not implemented now
}

function getAuthenticationKey(){
    // TODO: Use localStorage.setItem to save item
    let key = prompt("Please enter authentication key");
   
    if (key != null && key.trim() != ""){
        authenticationKey = key
    }
    else{
        alert("Authentication key needed");
        getAuthenticationKey();
    }
}
///////
//  Disable and enable model and analysis versions as well as the themes panel
//////
function disableModelChoices() {
    
    $("#newModel").addClass("disabled");

    $("#modelVersion").addClass("disabled");
    $("#modelVersion").attr("disabled", true);
    
}

function disableAnalysisChoices(){
    $("#newAnalysis").addClass("disabled");
    
    $("#analysisVersion").addClass("disabled");
    $("#analysisVersion").attr("disabled", true);
}

function enableModelChoices() {
    enableCreateModel();
 
    $("#modelVersion").removeClass("disabled");
    $("#modelVersion").attr("disabled", false);
   
}

function enableCreateModel() {

    // If enviroment configuration dictates that no new models are to be created,
    // never enable the create model button
    
    $("#newModel").removeClass("disabled");
    $("#newModel").attr("disabled", false);
}


function enableAnalysisChoices(){
    $("#newAnalysis").removeClass("disabled");
    $("#newAnalysis").attr("disabled", false);
    
    $("#analysisVersion").removeClass("disabled");
    $("#analysisVersion").attr("disabled", false);
}

function disableThemeButtons(){
    $("#exportAnalysis").addClass("disabled");
    $("#exportAnalysis").attr("disabled", true);

    $("#newTheme").addClass("disabled");
    $("#newTheme").attr("disabled", true);
    
    $("#sortTheme").addClass("disabled");
    $("#sortTheme").attr("disabled", true);
    
    $("#themeSearchButton").addClass("disabled");
    $("#themeSearchButton").attr("disabled", true);
    
    d3.select("#topicsList").selectAll("li").selectAll("textarea").each(function(){
                                                                        $(this).attr("disabled", true);
                                                                        $(this).addClass("textarea_disabled");
                                                                              })
}

function enableThemeButtons(){
    $("#exportAnalysis").removeClass("disabled")
    $("#exportAnalysis").attr("disabled", false);

    $("#newTheme").removeClass("disabled")
    $("#newTheme").attr("disabled", false);
    
    $("#sortTheme").removeClass("disabled")
    $("#sortTheme").attr("disabled", false);
    
    $("#themeSearchButton").removeClass("disabled")
    $("#themeSearchButton").attr("disabled", false);
    
    d3.select("#topicsList").selectAll("li").selectAll("textarea").each(function(){
                                                                        $(this).attr("disabled", false);
                                                                        $(this).addClass("textarea_disabled");
                                                                        })
}


///////
// Resize
///////

// Handles window resize
$(window).resize(function() {
    if(this.resizeTO) clearTimeout(this.resizeTO);
    this.resizeTO = setTimeout(function() {
        $(this).trigger("resizeEnd");
    }, 500);
});

$(window).bind("resizeEnd", function(){
	// Check if the resize really occurred
	var newWidth = $(window).width();
	var newHeight = $(window).height();
	
	if (newWidth != windowWidth
		|| newHeight != windowHeight) {
		windowWidth = newWidth;
		windowHeight = newHeight;
	} else {
		// Abort the handler
		return;
	}
		
	// Update the element sizes
	resizeContainers();
	
	// Update the links
	renderLinks();
});

// Resizes the containers based on the current window size
function resizeContainers() {
	var otherHeight = 0;
	$(".outer-element").each(function(){
		otherHeight += $(this).outerHeight(true);
	})
		
	// Several magic numbers below to account for heights of headers, spaces, etc.
	var maxAvailableHeight = windowHeight - otherHeight
		- parseInt($("body > div.container-fluid").css("margin-top")) - parseInt($("body > div.container-fluid").css("border-top-width"));
	var mainAvailableHeight = maxAvailableHeight - $("#mainPanelLower").outerHeight();
	
	// Adjust the sizes of the inner containers
	var innerAvailableHeight = mainAvailableHeight - TOP_OFFSET;
	$("#termsList, #topicsList, #themesList, #textsList").css("max-height", innerAvailableHeight + "px");
    
}



///////////////
/// For the panel above with datasets, models and analyses versions
///////////////

// Data set changes
//////

function populateDataChoices(){
    modelGetDataSetChoices();
}

function controllerDoPopulateDataChoices(choices){
    $("#dataset").empty();
    
    // Append the terms
    d3.select("#dataset").selectAll("option")
    .data(choices)
    .enter()
    .append("option")
    .each(function(d, i){
          let element = $(this);
          if (d.value == SELECTDATASETTEXT){
          element.attr("selected", true);
          element.attr("disabled", true);
          }
          element.attr("value", d.value);
          element.attr("title", d.value);
          //let titleLabel = $("<span></span>");
          //titleLabel.addClass("title-label");
          //titleLabel.append(d.term);
          element.append(d.value);
          });
    
}


function onDatasetChange() {
    var newDataset = $("#dataset").val();
    
    if (newDataset == modelCurrentDataset)
        return;
    
    resetInterface();
    disableAnalysisChoices();
    modelLoadModelForSelectedDataSet(newDataset);
    disableThemeButtons();
    
    
    
    // leads to controllerDoPopulateModelChoices via call-backs
    //resetDataWhenNewAnalysisIsSelected()
}

// invoked from the model
function controllerDoPopulateModelChoices(modelModelsForCurrentDataset){
    
    enableCreateModel();
    if (modelModelsForCurrentDataset != undefined && modelModelsForCurrentDataset != null && modelModelsForCurrentDataset.length > 1){
        enableModelChoices();
        $("#modelVersion").empty();
        
        // Append the options
        d3.select("#modelVersion").selectAll("option")
        .data(modelModelsForCurrentDataset)
        .enter()
        .append("option")
        .each(function(d, i){
              let element = $(this);
              element.attr("id", d.id)

              if (d.value == SELECTMODELTEXT){
              element.attr("selected", true);
              element.attr("disabled", true);
              }
              element.attr("value", d.value);
              element.attr("title", d.value);
              //let titleLabel = $("<span></span>");
              //titleLabel.addClass("title-label");
              //titleLabel.append(d.term);
              element.append(d.value);
              });
    }
    else{
        $("#modelVersion").addClass("disabled");
        $("#modelVersion").attr("disabled", true);
        
    }
}

/// Construct new model
function onConstructNewModel(){
    
    if (modelDisableModelCreation == undefined){
        var modelName = prompt("Please enter the name of the model to create");
    }
    else{
        var modelName = prompt("You are running with settings for which a new model cannot be created. You can load models that have been saved to file. Please specificy the model-id that you have been provided.");
    }
    if (modelName == null || modelName == "") {
        alert("No model created/loaded, a name must be given");
    } else {
        modelConstructNewModel(modelName);
        disableModelChoices();
        disableAnalysisChoices();
    }
}

/// Selection of models, and what results of that
///////////////////

function onModelVersionListChange(element) {
    var newModelVersionId  = $(this).children('option:selected').attr("id");
 
    
    if (newModelVersionId == modelCurrentModelId)
        return;
    
    resetInterface();
    disableThemeButtons();
    modelInitializeData(newModelVersionId);
    modelLoadAnalysesForSelectedModel(newModelVersionId);
    
    // leads to controllerDoPopulateInterface and controllerDoPopulateAnalysisChoices via call-backs to the model function 'doInitializeData'
    //resetDataWhenNewAnalysisIsSelected()
}

/// Selection of analyses
function onAnalysisVersionListChange(element) {
    
    var newAnalysisVersionId  = $(this).children('option:selected').attr("id");
    
    if (newAnalysisVersionId == modelCurrentAnalysisVersionId)
        return;
    
    modelLoadNewAnalysis(newAnalysisVersionId)
    // leads to controllerDoPopulateInterface and controllerDoPopulateThemes via call-backs
    //resetDataWhenNewAnalysisIsSelected()
}

// invoked from the model
function controllerDoPopulateAnalysisChoices(modelAnalysesForCurrentModel){
    if (modelAnalysesForCurrentModel != undefined && modelAnalysesForCurrentModel != null && modelAnalysesForCurrentModel.length > 1){
        enableAnalysisChoices();
        
        
        $("#analysisVersion").empty();
        
        // Append the options
        d3.select("#analysisVersion").selectAll("option")
        .data(modelAnalysesForCurrentModel)
        .enter()
        .append("option")
        .each(function(d, i){
              let element = $(this);
              element.attr("id", d.id)
              
              if (d.value == SELECTANALYSISTEXT){
              element.attr("selected", true);
              element.attr("disabled", true);
              }
              element.attr("value", d.value);
              element.attr("title", d.value);
              //let titleLabel = $("<span></span>");
              //titleLabel.addClass("title-label");
              //titleLabel.append(d.term);
              element.append(d.value);
              });
    }
    else{
        $("#analysisVersion").addClass("disabled");
        $("#analysisVersion").attr("disabled", true);
    }
}


function onNewAnalysis(){
    var analysisName = prompt("Please enter the name of the analysis to create");

    if (analysisName == null || analysisName == "") {
        alert("No new analysis created, a name must be given");
    } else {
    disableAnalysisChoices();
    modelConstructNewAnalysis(analysisName);

}
}

function onExportAnalysis(){
    modelExportAnalysis();
}



////




///////////
// Add data to interface
/////////

// Initializes/resets the interface
function resetInterface() {
	$("#termsList").empty();
	$("#topicsList").empty();
	$("#themesList").empty();
	$("#textsList").empty();
    
	resetLinks();
    hideSearchFields();
}

// Populates the interface
function controllerDoPopulateInterface() {
    
    //resetInterface();
    $("#termsList").empty();
    $("#textsList").empty();
    resetLinks();
    
    // Append the terms
	d3.select("#termsList").selectAll("li")
	.data(modelTerms)
	.enter()
	.append("li")
	.classed("list-group-item", true)
    
	.each(function(d, i){
		let element = $(this);
		element.addClass("term-element");
		element.attr("title", "Term: " + d.term);
		element.attr("style", "padding: 5px 7px;");
		let titleLabel = $("<span></span>");
		titleLabel.addClass("title-label");
		titleLabel.append(d.term.replace("_", " ").replace("_", " ").replace("_", " "));
   
		element.append(titleLabel);
        

	});
    
    // topics
    // only populate topics if no analysis is chosen. If an analysis is chosen, this will instead be performed in from the callback when loading an analysis version
    if (modelCurrentAnalysisVersionId == null){

        controllerDoPopulateTopicElements();
        disableThemeButtons(); // To disable the text areas of the topics, as they should be be changed when no theme is chosen
    }
    

    //texts
    controllerDoPopulateTextElements();
  
    adaptArgumentationButtonsToModel();
	// Themes are populated in  controllerDoPopulateThemes, when an analysis version is selected, and not here
   
    
    // Sort the lists initially
    doDefaultSort();
    
	// Resize the containers
	resizeContainers();
	
	// Draw the links over an SVG canvas
	renderLinks();
    
    // Disable term highlighting that are not to be there
    resetHighlight();
}

function controllerDoPopulateTextElements(){
    $("#textsList").empty();
    d3.select("#textsList").selectAll("li")
    .data(modelDocuments)
    .enter()
    .append("li")
    .classed("list-group-item", true)
    //.attr("draggable", true)
    .each(populateTextElement);
}

// For updating the label in one specific text element
function controllerDoPopulateOneTextElement(data){
    let selectEl = d3.select("#textsList").selectAll("li")
    .filter(function(f, j){
        return data.text_id == f.id;
        })
    let group = populateTextElementLabel(selectEl);
    
    let container = d3.select("#textsList").selectAll("li")
    .filter(function(f, j){
            return data.text_id == f.id;
            })
    .selectAll(".label-button-container")
    .each(function(d, i){
          let el = $(this);
          el.empty();
          el.append(group);
          })
    
}


function controllerDoPopulateTopicElements(){
    $("#topicsList").empty();
    // Append the topics
    d3.select("#topicsList").selectAll("li")
    .data(modelTopics)
    .enter()
    .append("li")
    .classed("list-group-item", true)
    .each(function(d, i){
          let element = $(this);
          
          element.addClass("topic-element");
          
          let titleLabel = $("<textarea  type=\"text\" class=\"form-control\"></textarea>");
          titleLabel.addClass("title-label");
          titleLabel.addClass("topic-input");
          titleLabel.attr("placeholder", "Topic #" + d.id);
          titleLabel.val(d.label);
          
          let userLabel = modelGetTopicNameForId(d.id);
          
          if(userLabel == undefined){
          // Use the default label
          titleLabel.val(d.defaultlabel);
          }
          else{
          // Use the user-defined label
          titleLabel.val(userLabel);
          }
          element.append(titleLabel);
          
          });
}


function onChooseLabelClick(event){
    let element = $(this);
    let userDefinedLabel = element.attr("id");
    let textId = element.attr("text-id");

    modelDefineUserLabel(textId, userDefinedLabel);

}

function populateTextElement(d, i){
    
    let element = $(this);
    element.empty(); // As this function is also used for repopulation, start with emptying what is there
    element.addClass("text-element");
    element.attr("title", "Document #" + d.base_name + ": " + d.label);
 
    let buttonGroup = populateTextElementLabel(d3.select(element.get(0)));
    let buttonGroupContainer = $("<span></span>");
    buttonGroupContainer.append(buttonGroup);
    buttonGroupContainer.addClass("label-button-container");
    buttonGroupContainer.attr("draggable", true)
    
    let textContainer = $("<p></p>");
    textContainer.append(buttonGroupContainer);
    textContainer.addClass("text-container");
    //textContainer.attr("draggable", true)
    element.append(textContainer);
    
    let textLabel = $("<div></div>");
    textLabel.append(d.marked_text_tok);
    textLabel.addClass("full-text");
    textLabel.addClass("not-displayed-text");
    textContainer.append(textLabel);
    
    let snippetLabel = $("<div></div>");
    snippetLabel.append(d.snippet);
    snippetLabel.addClass("snippet-text")
    snippetLabel.addClass("displayed-text")
    textContainer.append(snippetLabel);
    //textLabel.append("marked_text_tok" in d ? d.marked_text_tok : d.text);
    
    
    // Add additional labels
    let additionalLabelsContainer = $("<div></div>");
    additionalLabelsContainer.addClass("texts-info-container");
    populateAdditionalLabelsAtTextElement(d, additionalLabelsContainer);
    element.append(additionalLabelsContainer)
    
    // Add the info about the links between the text and the theme
    let themeTextContainer = $("<div></div>");
    themeTextContainer.addClass("theme-texts-container");
    populateThemeTextsContainerAtTextElement(d, themeTextContainer);
    element.append(themeTextContainer)

    colorAllTagsWithTheSameColor(element);
    
}

// Code for  displaying the label and the popup for changing it
function populateTextElementLabel(element){
    
    let systemLabel = element.datum().label;
    let textId = element.datum().id;
    
    let buttonGroup = $("<div></div>");
    buttonGroup.addClass("btn-group");
    buttonGroup.addClass("pull-right");

    if (modelCurrentAnalysisVersionId != null){
        let button = $("<span></span>");
        button.addClass("dropdown-toggle");
        button.attr("data-toggle", "dropdown");
        button.attr("aria-haspopup", "true");
        button.attr("aria-expanded", "false");
    
        let label_to_use = systemLabel
        if (modelGetTextLabelForId(textId) != undefined){
            label_to_use = modelGetTextLabelForId(textId);
        }
        let badgeLabel = getBadgeLabel(label_to_use);
        badgeLabel.addClass("badge-main-label");
        badgeLabel.addClass("choose-label-trigger");
    
    
        if (modelGetTextLabelForId(textId) != undefined){
            badgeLabel.addClass("badge-main-label-user-chosen");
        }
    
    
        let chooseSpan = $("<span></span>");
        chooseSpan.addClass("glyphicon");
        chooseSpan.addClass("glyphicon-sort-by-attributes");
        chooseSpan.addClass("choose-label-trigger");
        chooseSpan.addClass("choose-label-glyphicon");
    
        button.append(badgeLabel);
        badgeLabel.append(chooseSpan);
        //badgeLabel.append(chooseSpan);
    
        let dropdown = $("<ul></ul>");
        dropdown.addClass("choose-label-trigger");
        dropdown.addClass("dropdown-menu")
        for (let j = 0; j < modelLabelCategories.length; j++){
            let dropdownItem = $("<span></span>");
            dropdownItem.addClass("choose-label-trigger");
            let badge = getBadgeLabel(modelLabelCategories[j]["label"]);
            badge.attr("text-id", textId);
            badge.addClass("choose-label-trigger");
            badge.addClass("change-label-trigger");

            dropdown.append(badge);
            dropdown.append(dropdownItem);
    }
    
        buttonGroup.append(button);
        buttonGroup.append(dropdown);
    
    }
    else{
        let badgeLabel = getBadgeLabel(systemLabel);
        badgeLabel.addClass("badge-main-label");
        buttonGroup.append(badgeLabel);
    }

    return buttonGroup;
}

function getBadgeLabel(stanceCategory){

    for (let j = 0; j < modelLabelCategories.length; j++){
        //console.log(modelLabelCategories[j]["label"])
        if (stanceCategory == modelLabelCategories[j]["label"]){
            let badgeLabel = $("<span style='background-color:" + modelLabelCategories[j]["color"] + "'></span>");
            badgeLabel.addClass("badge");
            badgeLabel.addClass("text-badge");
            badgeLabel.attr("id", stanceCategory);
            if (stanceCategory.length > 2) {
            badgeLabel.append(stanceCategory.substring(0, 2))
            }
            //else if (stanceCategory.length == 2){
            //    badgeLabel.append(stanceCategory + " ");
            //}
            else if (stanceCategory.length == 1){
                badgeLabel.append(stanceCategory + " ");
            }
            else{
                badgeLabel.append(stanceCategory);
            }
            return badgeLabel;
        }
    }
}

function populateAdditionalLabelsAtTextElement(textElement, additionalLabelsContainer){
    for (let j = 0; j < textElement["additional_labels"].length; j++){
        //console.log(textElement["additional_labels"][j])
        let badgeLabel = getAdditionalLabel(textElement["additional_labels"][j]);
        badgeLabel.addClass("badge");
        badgeLabel.addClass("additional-label-badge");
        additionalLabelsContainer.append(badgeLabel);
    }
}

function getAdditionalLabel(text){
    let badgeLabel = $("<span></span>");
    badgeLabel.addClass("badge");
    badgeLabel.addClass("additional-label-badge");
    badgeLabel.append(text);
    return badgeLabel;
}

// Populates a theme element
function populateThemeElement(d, i) {
    let element = $(this);
    element.empty() // Since this function is used also for repopulation, start with removing current content
    element.addClass("theme-element");
    element.attr("title", "Theme #" + d.id + ": " + d.label);
	
    let removeButton = $("<button type=\"button\" class=\"btn btn-default btn-xs theme-remove-button\" aria-label=\"Remove theme without associated texts\" title=\"Remove theme without associated texts\">"
		+ "<span class=\"glyphicon glyphicon-remove\" aria-hidden=\"true\"></span>"
		+ "</button>");
    
    removeButton.addClass("pull-right");
    
    if (hasThemeAssociatedTexts(d.id)){
        removeButton.addClass("disabled");
    }
        
    let indexLabel = $("<span>Theme #</span>");
    indexLabel.addClass("index-label");
    indexLabel.append(d.id);
    indexLabel.addClass("pull-right");
     
    let themeTextContainer = $("<div></div>");
    themeTextContainer.addClass("theme-texts-container");
	
    if(showLabels){
        // Add the topic labels for the theme
        populateThemeTextsContainer(d, themeTextContainer);
    }
    
    let titleLabel = $("<textarea type=\"text\" class=\"form-control\"></textarea>");
    titleLabel.addClass("title-label");
    titleLabel.attr("placeholder", "Theme #" + d.id + " (click to add description)");
    titleLabel.val(d.label);
    
	
    element.append(removeButton);
    element.append(indexLabel);
    element.append(titleLabel);
    element.append(themeTextContainer);
}




// Populates a theme text container in a text element
function populateThemeTextsContainerAtTextElement(text, themeTextsContainer) {
    
    for (let j = 0; j < modelThemes.length; j++){

        let themeId = modelThemes[j].id;
        if (isAssociatedThemeText(themeId, text.id)){

            let textLabel = $("<span></span>");

            textLabel.addClass("theme-texts-label");
            textLabel.data("themeid", themeId);
            textLabel.data("textid", text.id);
            textLabel.attr("title", "Text #" + text.id + " in theme #" + themeId);
            textLabel.append("Theme #" + themeId + "&nbsp;");

            
            let removeButton = $("<button type=\"button\" class=\"btn btn-default btn-xs theme-text-remove-button \" aria-label=\"Remove text from theme\" title=\"Remove text from theme\">"
                                 + "<span class=\"glyphicon glyphicon-remove text-theme-remove-glyph\" aria-hidden=\"true\"  ></span>"
                                 + "</button>");
            textLabel.append(removeButton);
            textLabel.addClass("theme-indicator");
            themeTextsContainer.append(textLabel);

        }
    }
}


// Populates a text information in a themes container
function populateThemeTextsContainer(themeData, themeTextsContainer) {
    let themeId = themeData.id
    let theme = modelThemesToTexts[themeId]
    if (theme == undefined){
        // No texts associated with this theme
        return;
    }
    
    let labelContainers = {};
    for (let j = 0; j < modelLabelCategories.length; j++){
        labelContainers[modelLabelCategories[j]["label"]] = $("<div></div>");
        labelContainers[modelLabelCategories[j]["label"]].addClass("themes-label-container");
    }
    
    
    let additionalLabelsCounter = {};
	for (let i = 0; i < theme.texts.length; i++) {
        
        let label = getLabelForText(theme.texts[i])
        let textLabel = getBadgeLabel(label);
        labelContainers[label].append(textLabel);
        
        let additionalLabels = getAdditionalLabelsForText(theme.texts[i])
        for (let i = 0; i < additionalLabels.length; i++){
            if (!(additionalLabels[i] in additionalLabelsCounter)){
                additionalLabelsCounter[additionalLabels[i]] = 0
            }
            additionalLabelsCounter[additionalLabels[i]] = additionalLabelsCounter[additionalLabels[i]] + 1
        }
        
        for (let j = 0; j < modelLabelCategories.length; j++){
            themeTextsContainer.append(labelContainers[modelLabelCategories[j]["label"]])
        }
  
    }
    let additionalLabelsContainers = $("<div></div>");
    additionalLabelsContainers.addClass("themes-additiona-label-container");
    let additionalLabelList = Object.keys(additionalLabelsCounter).sort();
    for (let k = 0; k < additionalLabelList.length; k++){
        let addLabel = getAdditionalLabel(additionalLabelList[k]);
        addLabel.append(" (" + additionalLabelsCounter[additionalLabelList[k]] + ")")
        additionalLabelsContainers.append(addLabel);
    }
    themeTextsContainer.append(additionalLabelsContainers);
	
}

// Resets the links between the elements
function resetLinks() {
	$("#bgSvgContainer").empty();
}

d3.selection.prototype.moveToFront = function() {
    return this.each(function(){
                     this.parentNode.appendChild(this);
                     });
};

// Renders the links between the term/topic/text/theme elements
function renderLinks() {
	// Remove the highlighting just in case
	resetLinkHighlight();
	
	resetLinks();
			
	renderTermToTopicLinks();
    
    renderTopicToTextLinks();
   
	renderTextsToThemeLinks();
    
    // Fix to place the links behind the containers so that the user can scroll with mouse-drag
    d3.select("#bgSvgContainer").each(function(){
                               let parent = $(this).get(0).parentNode;
                                 parent.removeChild($(this).get(0));
                                parent.insertBefore($(this).get(0), parent.firstChild);

    })
 
}


// Renders terms-to-topics links
function renderTermToTopicLinks() {
	// If any of the lists is empty, return
	if ($("#termsList").children().length == 0
		|| $("#termsList > li.term-element:not(.not-displayed)").length == 0
		|| $("#topicsList").children().length == 0
		|| $("#topicsList > li.topic-element:not(.not-displayed)").length == 0)
		return;
  
	// Prepare the scales to map the score of the link
    let maxScore = getMaxTermScore();
 	let opacityScale = getOpacityScale(maxScore);
    let strokeWidthScale = getStrokeWidthScale(maxScore, TERM_TO_TOPIC_LINK_WIDTHS);
 
	// Get the position of the first term element and the first topic element
	let firstTermElement = $("#termsList > li.term-element:not(.not-displayed):first");
	let firstTopicElement = $("#topicsList > li.topic-element:not(.not-displayed):first");

    let svgId = "termLinksSvg";
	let termLinks = prepareCanvasForLinks(firstTermElement, firstTopicElement, svgId, "termLinksHighlight");
			
	d3.select("#termsList").selectAll("li:not(.not-displayed)")
	.each(function(d, i){
        if (!(d.term in modelTermsToTopics))
          return;

        let leftElement = $(this);
		let relevantTopics = modelTermsToTopics[d.term].topics;
		
		d3.select("#topicsList").selectAll("li:not(.not-displayed)")
		.filter(function(e){ return relevantTopics.indexOf(e.id) > -1;})
		.each(function(e, j){
			let rightElement = $(this);
            let termScore = modelTermsToTopics[d.term].score_for_topics[modelTermsToTopics[d.term].topics.indexOf(e.id)]
            let text = "Topic #" + e.id + "\n" + "Term: " + d.term + "\n" + "Score: " + termScore
            drawLinks(leftElement, rightElement, termScore,
                      opacityScale, strokeWidthScale, termLinks,
                      { term: d.term, topic: e.id }, text, "terms-to-topics", svgId);
		});
	});
}

// Renders topics-to-text links
function renderTopicToTextLinks() {
    // If any of the lists is empty, return
    if ($("#textsList").children().length == 0
    	|| $("#textsList > li.text-element:not(.not-displayed)").length == 0
        || $("#topicsList").children().length == 0
        || $("#topicsList > li.topic-element:not(.not-displayed)").length == 0)
        return;
    
    // Prepare the scales to map the score of the link
    var maxScore = getMaxDocumentScore();
    let opacityScale = getOpacityScale(maxScore);
    let strokeWidthScale = getStrokeWidthScale(maxScore, TOPIC_TO_TEXT_LINK_WIDTHS)

 
    // Get the position of the first term element and the first topic element
    let firstTextElement = $("#textsList > li.text-element:not(.not-displayed):first");
    let firstTopicElement = $("#topicsList > li.topic-element:not(.not-displayed):first");
 
    let svgId = "textLinksSvg"
    let links = prepareCanvasForLinks(firstTopicElement, firstTextElement, svgId, "topicTextLinksHighlight")
    
    d3.select("#topicsList").selectAll("li:not(.not-displayed)")
    .each(function(d, i){
          let topicElement = $(this);
          
          if (!(d.id in modelTopicsToDocuments))
          return;
          
          let relevantDocuments = modelTopicsToDocuments[d.id].documents;
   
          d3.select("#textsList").selectAll("li:not(.not-displayed)")
          .filter(function(e){ return relevantDocuments.indexOf(e.id) > -1;})
          .each(function(e, j){
                let documentElement = $(this);
                
                // Detect the score
                var strokeScore = modelTopicsToDocuments[d.id].topic_confidences[modelTopicsToDocuments[d.id].documents.indexOf(e.id)]
                
                drawLinks(topicElement, documentElement, strokeScore,
                          opacityScale, strokeWidthScale, links,
                          { topic: d.id, document: e.id }, "Document #" + e.id + "\n"
                          + "Topic #" +d.id, "topics-to-texts", svgId);
                });
          });
}


// Renders topics-to-themes links
function renderTextsToThemeLinks() {
    // If any of the lists is empty, return
    if ($("#textsList").children().length == 0
    	|| $("#textsList > li.text-element:not(.not-displayed)").length == 0	
        || $("#themesList").children().length == 0
        || $("#themesList > li.theme-element:not(.not-displayed)").length == 0)
        return;
    
    // Prepare the scales to map the score of the link
    var maxScore = 1;
    let opacityScale = getOpacityScale(maxScore);
    let strokeWidthScale = getStrokeWidthScale(maxScore, TEXT_THEME_LINK_WIDTHS)
    
    
    // Get the position of the first topic element and the first theme element
    let firstTextElement = $("#textsList > li.text-element:not(.not-displayed):first");
    let firstThemeElement = $("#themesList > li.theme-element:not(.not-displayed):first");
    
    let svgId = "themeLinksSvg"
    let links = prepareCanvasForLinks(firstTextElement, firstThemeElement, svgId, "themeLinksHighlight")
    
    d3.select("#themesList").selectAll("li:not(.not-displayed)")
    .each(function(d, i){
          let themeElement = $(this);
          
          if (modelThemesToTexts[d.id] == undefined){
            return;
          }
          
          let relevantTexts = modelThemesToTexts[d.id].texts;
          let relevantTextsInts = []

          for (let i = 0; i < relevantTexts.length; i++){
                relevantTextsInts[i] = parseInt(relevantTexts[i])
          }
    
          
          d3.select("#textsList").selectAll("li:not(.not-displayed)")
          .filter(function(e) {
                  return relevantTextsInts.indexOf(parseInt(e.id)) > -1;})
          .each(function(e, j){
                let textElement = $(this);
                
                drawLinks(textElement, themeElement, 1,
                          opacityScale, strokeWidthScale, links,
                          { text: e.id, theme: d.id }, "Theme #" + d.id + "\n"
                          + "Text #" + e.id, "texts-to-themes", svgId);
                });
            });
}

//////
// Help functions for drawing the links
///////////


// Prepare the canvas and get the links
///

function getOpacityScale(maxScore){
    return d3.scale.linear().domain([0, maxScore]).range([0, 1]);
}

function getStrokeWidthScale(maxScore, linkWidths){
    return d3.scale.linear().domain([0, maxScore]).range(linkWidths);

}
function prepareCanvasForLinks(firstLeftElement, firstRightElement, svgId, linksHighlightId){

    // Get the offset of the SVG element with regard to its parent container
	let svgLeft = Math.ceil(firstLeftElement.offset().left
				+ firstLeftElement.parent().scrollLeft()
		 		- $("#bgSvgContainer").offset().left
				+ firstLeftElement.outerWidth());
	let svgTop = Math.ceil(firstLeftElement.offset().top
				+ firstLeftElement.parent().scrollTop()
				- $("#bgSvgContainer").offset().top);
		
	let svgWidth = Math.ceil(firstRightElement.offset().left
				- (firstLeftElement.offset().left + firstLeftElement.outerWidth())
		 		- 1);
	let svgHeight = Math.ceil($("#mainPanelUpper").height() - svgTop);
	
	let svg = d3.select("#bgSvgContainer").append("svg:svg")
				.classed("svg-vis", true)
				.attr("id", svgId)
				.style("top", svgTop + "px")
				.style("left", svgLeft + "px")
				.attr("height", svgHeight + "px")
				.attr("width", svgWidth + "px")
				.attr("clip", [0, svgWidth, svgHeight, 0].join(" "));
	
	// Prepare the clipping path for inner canvas
	svg.append("clipPath")
		.attr("id", "canvasClip")
	.append("rect")
	    .attr("x", 0)
	    .attr("y", 0)
	    .attr("width", svgWidth)
	    .attr("height", svgHeight);
	
	let canvas = svg.append("g")
		.classed("canvas-vis", true)
		.attr("clip-path", "url(#canvasClip)");
    
  		
    let links = canvas.append("g")
    .attr("id", "termLinks");
    
    // Add an overlay for highlighting
    canvas.append("g")
    .attr("id", linksHighlightId);
    
     //for debugging
    /*
     canvas.append("rect")
	    .attr("x", 0)
	    .attr("y", 0)
	    .attr("width", svgWidth)
	    .attr("height", svgHeight)
     .style("fill", "lightgreen");*/
    
    
    return links;
}

// Draw the actual lines
function drawLinks(leftElement, rightElement, termScore,
                opacityScale, strokeWidthScale, links,
                   datum, text, className, svgId){
    
    // Draw the links from terms to topics
    let offsetLeft = $("#" + svgId).offset().left;
    let offsetTop = $("#" + svgId).offset().top;
    
    // Get the port position (this is only needed  to be calculated once, so if things get slow, do earlier)
    let leftPortX = leftElement.offset().left - offsetLeft + leftElement.outerWidth();
    let leftPortY = leftElement.offset().top - offsetTop + Math.floor(leftElement.outerHeight()/2);
              
    // Get the port position
    let rightPortX = rightElement.offset().left - offsetLeft;
    let rightPortY = rightElement.offset().top - offsetTop + Math.floor(rightElement.outerHeight()/2);
		
    
    
    // Draw the link
    links.append("line")
            .classed(className, true)
            .datum(datum)
            .attr("x1", leftPortX)
            .attr("y1", leftPortY)
            .attr("x2", rightPortX)
            .attr("y2", rightPortY)
            .style("stroke-opacity", opacityScale(termScore))
            .style("stroke", strokeWidthScale(termScore))
            .style("stroke", "black")
            .append("svg:title")
            .text(text);
}



/////////
// Listener functions
//////////

// Updates the links on list scroll
// Set a timer so that the links will not always be updated when scrolling, as this slows down the scrolling
var timer = null;
function onListScroll() {
	//renderLinks();
    if(timer !== null) {
        clearTimeout(timer);
    }
    timer = setTimeout(function() {
        renderLinks();
    }, 200);
}



// Reacts to the topic label change
function onTopicRename() {
	let newLabel = $(this).val();
	let topicElement = $(this).parent(".topic-element");
	
	// Update the corresponding data element
	let topic = d3.select(topicElement.get(0)).datum();
	topic.label = newLabel;
	// Update the tooltip
	topicElement.attr("title", "Topic #" + topic.id + ": " + topic.label);
	
    modelRenameTopic(topic.id, newLabel);
}

// Reacts to the theme label change
function onThemeRename() {
    let newLabel = $(this).val();
    let themeElement = $(this).parent(".theme-element");
	
    // Update the corresponding data element
    let theme = d3.select(themeElement.get(0)).datum();
    theme.label = newLabel;
    // Update the tooltip
    themeElement.attr("title", "Theme #" + theme.id + ": " + theme.label);
	
    modelRenameTheme(theme.id, newLabel)
}

// Reacts to the sort trigger
function onSortDocumentsList(event) {
    event.preventDefault();
    modelResetClickedChoices();
    
    lockTextsSorting = true;
    onLockTextSorting(); // onLockTextSorting always toggles the value of lockTextsSorting, so these two will unlock it

    let sortKey = $(this).data("sortkey");
	
    // Update the global sort mode
    textSortMode = sortKey;
	
    // Update the visible checkmark
    $(".sort-documents-trigger > span.checkmark").empty();
    $(".sort-documents-trigger[data-sortkey='" + sortKey + "']").children("span.checkmark").html("&#x2713;");
	
    sortTextsList(sortKey);
	
    // Redraw the links and reset highlight
    resetHighlightAfterStateChange();
    resetHighlight();
    renderLinks();
}


// Reacts to the sort trigger
function onSortTermsList(event) {
    event.preventDefault();
    modelResetClickedChoices();

    lockTermsSorting = true;
    onLockTermsSorting(); // onLockTermsSorting always toggles the value of lockTermsSorting, so these two will unlock it

    let sortKey = $(this).data("sortkey");
	
    // Update the global sort mode
    termSortMode = sortKey;
	
    // Update the visible checkmark
    $(".sort-terms-trigger > span.checkmark").empty();
    $(".sort-terms-trigger[data-sortkey='" + sortKey + "']").children("span.checkmark").html("&#x2713;");
		
    sortTermsList(sortKey);
	
    // Redraw the links and reset highlight
    resetHighlightAfterStateChange();
    resetHighlight();
    renderLinks();
}



// Reacts to the sort trigger
function onSortTopicsList(event) {
    event.preventDefault();
    modelResetClickedChoices();

    lockTopicsSorting = true;
    onLockTopicsSorting(); // onLockTopicsSorting always toggles the value of lockTermsSorting, so these two will unlock it

	
    let sortKey = $(this).data("sortkey");
	
    // Update the global sort mode
    topicSortMode = sortKey;
	
    // Update the visible checkmark
    $(".sort-topics-trigger > span.checkmark").empty();
    $(".sort-topics-trigger[data-sortkey='" + sortKey + "']").children("span.checkmark").html("&#x2713;");
		
    sortTopicsList(sortKey);
	
    // Redraw the links and reset highlight
    resetHighlightAfterStateChange();
    resetHighlight();
    renderLinks();
}

// Reacts to the sort trigger
function onSortThemesList(event) {
    modelResetRecentlyClickedForMachineLearningSorting();
    modelResetClickedChoices();
    
	event.preventDefault();
	
	let sortKey = $(this).data("sortkey");
	
	// Update the global sort mode
	themeSortMode = sortKey;
	
	// Update the visible checkmark
	$(".sort-themes-trigger > span.checkmark").empty();
	$(".sort-themes-trigger[data-sortkey='" + sortKey + "']").children("span.checkmark").html("&#x2713;");
			
	sortThemesList(sortKey);
	
    // Redraw the links and reset highlight
    resetHighlightAfterStateChange();
    resetHighlight();
    renderLinks();
}




///////
// Sort functions
//////

function scrollTopForAllExceptRecentlyClicked(recentlyClicked){

    if (! (recentlyClicked == "#termsList")){
        let termsContainer = $("#termsList");
        termsContainer.scrollTop(0);
    }
    
    if (! (recentlyClicked == "#textsList")){
        let textsContainer = $("#textsList");
        textsContainer.scrollTop(0);
        }
    
    if (! (recentlyClicked == "#topicsList")){
        let topicsContainer = $("#topicsList");
        topicsContainer.scrollTop(0);
    }
    
    if (! (recentlyClicked == "#themesList")){
        let themesContainer = $("#themesList");
        themesContainer.scrollTop(0);
    }
    
}

// Sorts the terms list
function sortTermsList(sortKey) {
	if (!(sortKey in SORT_TERMS))
		return;
	
	// Use the external sorting function for the terms list
	let sortFunction = SORT_TERMS[sortKey];
	
	let termsContainer = $("#termsList");
	let termElements = termsContainer.children("li.term-element").detach();
	let sortedElements = sortFunction(termElements);
	// Reset the scrolling for the container before reattaching the elements
	//termsContainer.scrollTop(0);
	termsContainer.append(sortedElements);
}



// Sorts the text list
function sortTextsList(sortKey) {
    if (!(sortKey in SORT_TEXT))
        return;
    
    // Use the external sorting function for the terms list
    let sortFunction = SORT_TEXT[sortKey];
    
    let textsContainer = $("#textsList");
    let textsElements = textsContainer.children("li.text-element").detach();
    let sortedElements = sortFunction(textsElements);
    // Reset the scrolling for the container before reattaching the elements
    //textsContainer.scrollTop(0);
    textsContainer.append(sortedElements);
}

// Sorts the topic list
function sortTopicsList(sortKey) {
    if (!(sortKey in SORT_TOPIC))
        return;
    
    // Use the external sorting function for the terms list
    let sortFunction = SORT_TOPIC[sortKey];
    
    let topicsContainer = $("#topicsList");
    let topicsElements = topicsContainer.children("li.topic-element").detach();
    let sortedElements = sortFunction(topicsElements);
    // Reset the scrolling for the container before reattaching the elements
    //topicsContainer.scrollTop(0);
    topicsContainer.append(sortedElements);
}

// Sorts the theme list
function sortThemesList(sortKey) {
    if (!(sortKey in SORT_THEME))
        return;
    
    // Use the external sorting function for the terms list
    let sortFunction = SORT_THEME[sortKey];

    
    let themesContainer = $("#themesList");
    let themesElements = themesContainer.children("li.theme-element").detach();
    let sortedElements = sortFunction(themesElements);
    // Reset the scrolling for the container before reattaching the elements
    //themesContainer.scrollTop(0);
    themesContainer.append(sortedElements);
}



////
// For selecting itmes
////

function fillSplittedCurrentTermList(){
    // Split to be able to mark synonyms and multiword expressions in the text
    splittedTerms = []
    for (let j = 0; j < currentTermIds.length; j++){
        let splitted1 = currentTermIds[j].split("/")
        for (let k = 0; k < splitted1.length; k++){
            let comp1 = splitted1[k].trim();
            let splitted2 = comp1.split("_");
            for (let l = 0; l < splitted2.length; l++){
                let comp2 = splitted2[l].trim();
                splittedTerms.push(comp2);
            }
        }
    }
}

function onTermElementClick(){

    let term = d3.select($(this).get(0)).datum();
    
    toggleChosenElement(term.term, modelToggleTermElement);
    
    if (currentTermIds.indexOf(term.term) > -1){ // if chosen
        $(this).addClass(DIRECTCHOOSEN);
        setTimeout(highlightTermElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    else{
        $(this).removeClass(DIRECTCHOOSEN);
        setTimeout(highlightTermElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    
    // For the other panels, which were not recently clicked, they should show the beginning of the panel, so scroll up
    scrollTopForAllExceptRecentlyClicked("#termsList");

    
    // Sort other lists and render the links
    

    setTimeout(resetPanelHeadings(), 0);
    setTimeout(setPanelHeadings(), 0);
    setTimeout(resetHighlightAfterStateChange(), 0);
}

function onTopicElementClick(){
    let eventClass = $(event.target).attr("class");
    if (eventClass.includes("title-label")){
        // Discard clicks on the subcomponents within a topic element
        return;
    }
	
    let topic = d3.select($(this).get(0)).datum();
    toggleChosenElement(topic.id, modelToggleTopicElement);

    if (currentTopicIds.indexOf(topic.id) > -1){ // if chosen
        $(this).addClass(DIRECTCHOOSEN);
        setTimeout(highlightTopicElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    else{
        $(this).removeClass(DIRECTCHOOSEN);
        setTimeout(highlightTopicElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    
    // For the other panels, which were not recently clicked, they should show the beginning of the panel, so scroll up
    scrollTopForAllExceptRecentlyClicked("#topicsList");
    
    setTimeout(resetPanelHeadings(), 0);
    setTimeout(setPanelHeadings(), 0);
    
    setTimeout(resetHighlightAfterStateChange(), 0);
}

function onTextElementClick(){
    let eventClass = $(event.target).attr("class");
    if (eventClass.includes("choose-label-trigger") || eventClass.includes("theme-text-remove-button") || eventClass.includes("text-theme-remove-glyph") || eventClass.includes("text-container")){
        // Discard clicks on the subcomponents within a text element
        return;
    }
    
    let text = d3.select($(this).get(0)).datum();
    toggleChosenElement(text.id, modelToggleTextElement);
    
    
    // Sort other lists and render the links
    
    if (currentTextIds.indexOf(text.id) > -1){ // if chosen
        $(this).addClass(DIRECTCHOOSEN);
        setTimeout(highlightTextElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    else{
        $(this).removeClass(DIRECTCHOOSEN);
        setTimeout(highlightTextElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    
    // For the other panels, which were not recently clicked, they should show the beginning of the panel, so scroll up
    scrollTopForAllExceptRecentlyClicked("#textsList");
    
    modelSetMostRecentlyClickedForThemeRanking(text.id);
    //This sorting the rendering is not done here, but in a call-back from modelGetThemeRankingForText
    //sortThemesList(themeSortMode);
    //renderLinks();
    setTimeout(resetPanelHeadings(), 0);
    setTimeout(setPanelHeadings(), 0);
    
    setTimeout(resetHighlightAfterStateChange(), 0);
    
   
}

function onThemeElementClick(event){
    let eventClass = $(event.target).attr("class");
    if (eventClass != undefined && (eventClass.includes("title-label") || eventClass.includes("glyphicon"))){
        // Discard clicks on the subcomponents within a theme element
        return;
    }
    
    let theme = d3.select($(this).get(0)).datum();
    toggleChosenElement(theme.id, modelToggleThemeElement);
    
    if (currentThemeIds.indexOf(theme.id) > -1){ // if chosen
        $(this).addClass(DIRECTCHOOSEN);
        setTimeout(highlightThemeElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    else{
        $(this).removeClass(DIRECTCHOOSEN);
        setTimeout(highlightThemeElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    
    // For the other panels, which were not recently clicked, they should show the beginning of the panel, so scroll up
    scrollTopForAllExceptRecentlyClicked("#themesList");
    setTimeout(resetPanelHeadings(), 0);
    setTimeout(setPanelHeadings(), 0);
    
    setTimeout(resetHighlightAfterStateChange(), 0);
}



// Help function used by all all element click functions to toggle between chosen or not
function toggleChosenElement(id, modelToggleFunction){
    modelToggleFunction(id);
    fillSplittedCurrentTermList();
    //doDefaultSort(); // Note: appropriate sorting is triggered elsewhere
    //HERE
    //resetHighlightAfterStateChange();
    resetHighlight();
}


function doDefaultSort(){
	// Set the global sort modes and sort the lists accordingly
	termSortMode = "score/desc";
	topicSortMode = "score/desc";
	textSortMode = "score/desc";
	themeSortMode = "time/desc";
	
	// Update the visible checkmarks
	$("span.checkmark").empty();
	$(".sort-terms-trigger[data-sortkey='" + termSortMode + "']"
	  + ", " + ".sort-topics-trigger[data-sortkey='" + topicSortMode + "']"
	  + ", " + ".sort-documents-trigger[data-sortkey='" + textSortMode + "']"
	  + ", " + ".sort-themes-trigger[data-sortkey='" + themeSortMode + "']"
	  ).children("span.checkmark").html("&#x2713;");
	
    sortTermsList(termSortMode);
    sortTopicsList(topicSortMode);
    sortTextsList(textSortMode);
    sortThemesList(themeSortMode);
}


// Drag texts
// Handles the text element drag start event
function onTextElementDragStart(event) {
    let eventClass = $(event.target).attr("class");
    if (eventClass.includes("text-container")){
        // Discard drag on text element
        return;
    }
    
	let originalEvent = event.originalEvent;
	let textElement = $(event.target).parentsUntil("#textsList", ".text-element");
    //alert(textElement);
	// Mark the element as the source of dragged data
	// (used for filtering in dragover handlers, since there is no way to access the data)
    textElement.addClass("dragged");

 		
	let transferData = {
	    //textId: d3.select(event.target).datum().id
	    textId: d3.select(textElement.get(0)).datum().id
	};
   
	originalEvent.dataTransfer.setData("text-element", JSON.stringify(transferData));
	originalEvent.dataTransfer.effectAllowed = "copy";
	originalEvent.dataTransfer.dropEffect = "copy";
}


// Handles the text element drag end event
function onTextElementDragEnd(event) {
	let originalEvent = event.originalEvent;
	let textElement = $(event.target);
	
	originalEvent.dataTransfer.clearData();
	
	// Unmark the element as the source of dragged data
	textElement.removeClass("dragged");
}





// Handles the theme element drag enter event
// Note: the transfer data is not available in this method due to browser security concerns
// TODO: The same function is used for "enter" and "over", doulbe-check that this works
function onThemeElementDragEnterOver(event) {
	let originalEvent = event.originalEvent;
	let themeElement = $(event.currentTarget);
	
    if (!originalEvent.dataTransfer.types.includes("text-element")){
		return;
    }
	
    if (originalEvent.dataTransfer.types.includes("text-element")){
        
        let draggedTextElement = $("#textsList .text-element.dragged");
        if (draggedTextElement.length == 0)
            return;
        
        
        let draggedText = d3.select(draggedTextElement.get(0)).datum();
        if (!draggedText)
            return;
        
        let currentTheme = d3.select(themeElement.get(0)).datum();
        
        themeElement.addClass("drop-feedback");

        originalEvent.dataTransfer.dropEffect = "copy";
        originalEvent.preventDefault();
       
        return false;

    }
    

}

// Handles the theme element drag over event
// Note: the transfer data is not available in this method due to browser security concerns
/*
function onThemeElementDragOver(event) {
    
	let originalEvent = event.originalEvent;
	let themeElement = $(event.currentTarget);
	
    if (!originalEvent.dataTransfer.types.includes("text-element")){
        return;
    }

    if (originalEvent.dataTransfer.types.includes("text-element")){
        
        let draggedTextElement = $("#textsList .text-element.dragged");
        if (draggedTextElement.length == 0)
            return;
        
        let draggedText = d3.select(draggedTextElement.get(0)).datum();
        if (!draggedText)
            return;
        
        let currentTheme = d3.select(themeElement.get(0)).datum();
        
        // If it is already a connection bewteen document and theme, discard
        if (modelThemesToTexts[currentTheme.id] != undefined &&
            modelThemesToTexts[currentTheme.id].texts.indexOf(draggedText.id) > -1){
            return;
        }
        themeElement.addClass("drop-feedback");
        
        originalEvent.dataTransfer.dropEffect = "copy";
        originalEvent.preventDefault();
        return false;
    }
    
}
 */

// Handles the theme element drag leave event
function onThemeElementDragLeave(event) {
	let themeElement = $(event.currentTarget);
    themeElement.removeClass("drop-feedback");
}

// Handles the theme element drop event
function onThemeElementDrop(event) {
	let originalEvent = event.originalEvent;
	originalEvent.stopPropagation();
	

	let themeElement = $(event.currentTarget);
    themeElement.removeClass("drop-feedback");

 
    if (originalEvent.dataTransfer.types.includes("text-element")){
        let transferData;
        try {
            transferData = JSON.parse(originalEvent.dataTransfer.getData("text-element"));
         } catch (e) {
            console.error(e);
            return false;
        }
        
        // Handle the successful drop
        onSuccessfulThemeTextElementDrop(themeElement, transferData.textId);
    }
	return false;
}


// Handles the successful drag'n'drop for a topic element and a theme element
function onSuccessfulThemeTextElementDrop(themeElement, textId) {
    
    // Get the theme element datum
    let theme = d3.select(themeElement.get(0)).datum();
    modelAddTextThemeLink(theme.id, textId)
    
    //addTextTheme(theme.id)
    
    // Repopulate the theme element for the updated text-theme links
    d3.select("#themesList").selectAll("li")
    .filter(function(f, j){
            return theme.id == f.id;
            })
    .each(populateThemeElement);
    
    
    // Adds information of associated themes to the text elements
    d3.select("#textsList").selectAll("li")
    .filter(function(f, j){
            return isAssociatedThemeText(theme.id, f.id);
            })
    .each(populateTextElement);
    
    addChoiceBasedHighlight();
    
    //doDefaultSort(); // XXX: disabled not to disturb the user (imagine someone in the middle of a very long list...)
    // Redraw the links
    renderLinks();
}


// Removes a text from a theme
function onThemeTextRemoveAtTextElement(){
	let textElement = $(this).parentsUntil("#textsList", ".text-element");
	
	// Update the corresponding data element
	let text = d3.select(textElement.get(0)).datum();
    
    if (!text){
        console.error("no text")
		return;
    }
    
    
	let themeLabel = $(this).parent(".theme-texts-label");
    let themeId = themeLabel.data("themeid")
    
    removeTextThemeLink(themeId, text.id);
    
    // Repopulate the text element for the updated text-theme links
    d3.select("#textsList").selectAll("li")
    .filter(function(f, j){
            return text.id == f.id;
            })
    .each(populateTextElement);
    
    // Repopulate the theme element for the updated text-theme links
    d3.select("#themesList").selectAll("li")
    .filter(function(f, j){
            return themeId == f.id;
            })
    .each(populateThemeElement);
    
	// Redraw the links
	renderLinks();
    
}

// Creates a new theme
function onThemeAdd() {
	createNewTheme();	
}

// Creates a new theme with an optionally provided list of text IDs
function createNewTheme(textIds) {
    modelCreateNewTheme(textIds);
}

function controllerSelectChosenAnalysis(name_of_created_analysis){
    
    $("#analysisVersion").val(name_of_created_analysis);
    $("#analysisVersion").trigger("change");
}

function controllerDoPopulateThemes(doSorting){
    $("#themesList").empty();
	// Update the list elements with D3
	d3.select("#themesList").selectAll("li")
	// Note the function below used to ensure the correct mapping of existing elements
	// despite the arbitrary DOM ordering after sorting
	.data(modelThemes, function(d) { return d.id; })
	.enter()
	.append("li")
	.classed("list-group-item", true)
	.each(populateThemeElement);
	
    if (doSorting){
        doDefaultSort();
    }
    
    // Resize the containers
    resizeContainers();
    
    // Redraw the links
    renderLinks();
    
    enableThemeButtons();
}

// Removes a theme
function onThemeRemove() {
    let themeElement = $(this).parentsUntil("#themesList", ".theme-element");
	
	// Get the corresponding data element
	let theme = d3.select(themeElement.get(0)).datum();
	if (!theme)
		return;
	
    // Remove theme in the model
    let removeResult = removeTheme(theme.id);
    
    if (!removeResult){
        return; // It is not allowed to delete themes that have associated texts.
    }
	// Remove the theme element
	themeElement.remove();
		
    resetHighlight();
    // Redraw the links
	renderLinks();
}



// Resets highlighting
function resetHighlight() {
    
    d3.selectAll("." + HIGHLIGHT)
     .classed(HIGHLIGHT, false);
    
    d3.selectAll("." + DIRECTHIGHLIGHT)
    .classed(DIRECTHIGHLIGHT, false);

    
    resetLinkHighlight();
}

// Resets highlighting
var resetHighlightTimer = null;
// Don't do many resets, if many choices are made by the user in a short period of time, wait unti the last choice has been made
function resetHighlightAfterStateChange(){
    if(resetHighlightTimer != null){
        clearTimeout(resetHighlightTimer)
    }
    resetHighlightTimer = setTimeout(doResetHighlightAfterStateChange, 0)
}

function doResetHighlightAfterStateChange(){
    // If a term is not selected
    if (currentTermIds.length == 0){
        sortTermsList(termSortMode);
    }
    
    // If a topic is not selected
    if (currentTopicIds.length == 0){
        sortTopicsList(topicSortMode);
    }
    
    // If a text is not selected
    if (currentTextIds.length == 0){
        sortTextsList(textSortMode);
    }
    
    // If a theme is not selected
    if (currentThemeIds.length == 0){
        modelSortThemesWithMachineLearningIfTextChosen();
        //sortThemesList(themeSortMode);
    }
    
    renderLinks();
    
    setTimeout(addChoiceBasedHighlight, 1);
    
}


function resetPanelHeadings(){
    d3.select("#termsContainer").select(".panel-heading").classed("panel-heading-marked", false);
    d3.select("#topicsContainer").select(".panel-heading").classed("panel-heading-marked", false);
    d3.select("#textContainer").select(".panel-heading").classed("panel-heading-marked", false);
    d3.select("#themesContainer").select(".panel-heading").classed("panel-heading-marked", false);
    
    d3.select("#termsContainer").classed("panel-marked", false);
    d3.select("#topicsContainer").classed("panel-marked", false);
    d3.select("#textContainer").classed("panel-marked", false);
    d3.select("#themesContainer").classed("panel-marked", false);
}

function setPanelHeadings(){
    if (currentTermIds.length > 0){
        d3.select("#termsContainer").select(".panel-heading").classed("panel-heading-marked", true);
        d3.select("#termsContainer").classed("panel-marked", true);
    }
    if (currentTopicIds.length > 0){
        d3.select("#topicsContainer").select(".panel-heading").classed("panel-heading-marked", true);
        d3.select("#topicsContainer").classed("panel-marked", true);
    }
    if (currentTextIds.length > 0){
        d3.select("#textContainer").select(".panel-heading").classed("panel-heading-marked", true);
        d3.select("#textContainer").classed("panel-marked", true);
    }
    if (currentThemeIds.length > 0){
        d3.select("#themesContainer").select(".panel-heading").classed("panel-heading-marked", true);
        d3.select("#themesContainer").classed("panel-marked", true);
    }
}

function resetLinkHighlight() {
    d3.selectAll(".link-highlight, .link-direct-highlight")
    .classed("link-highlight", false)
    .classed("link-direct-highlight", false);
    
    d3.selectAll(".link-overlay-highlight, .link-overlay-direct-highlight, " +
                 ".link-overlay-highlight-bg, .link-overlay-direct-highlight-bg")
    .remove();

}


function addChoiceBasedHighlight(){
    
    // If there are selected items, first set all items to grey
    
    /*
    if (currentTermIds.length > 0 ||
        currentTopicIds.length > 0 ||
        currentTextIds.length > 0 ||
        currentThemeIds.length > 0){
        d3.select("#termsList").selectAll("li").classed(NOTCHOSEN, true);
        d3.select("#topicsList").selectAll("li").classed(NOTCHOSEN, true);
        d3.select("#textsList").selectAll("li").classed(NOTCHOSEN, true);
        d3.select("#themesList").selectAll("li").classed(NOTCHOSEN, true);
    }*/
    

    
    d3.selectAll("." + DIRECTCHOOSEN)
    .classed(DIRECTCHOOSEN, false);
    
    d3.selectAll("." + CHOOSEN)
    .classed(CHOOSEN, false);
    
    d3.selectAll("." + NOTCHOSEN)
    .classed(NOTCHOSEN, false);
    
    d3.selectAll('.snippet-text').classed("not-displayed-text", false);
    d3.selectAll('.full-text').classed("not-displayed-text", true);

    d3.selectAll('.snippet-text').classed("displayed-text", true);
    d3.selectAll('.full-text').classed("displayed-text", false);


    d3.selectAll('.text-container').classed("text-border", false);
    
    // Reset highlight of terms that stem from topics that are not chosen
    
    d3.selectAll(".term-to-mark").classed("specifictermchosen", true);
    d3.selectAll(".term-to-mark").classed("termintextnotchosen", true);
    // Then go through all items to see which are selected
    // and set them to not grey
    
    d3.select("#termsList").selectAll("li")
    .each(function(d, i){
          let element = $(this);
          if (currentTermIds.indexOf(d.term) > -1){
            highlightTermElement(element, DIRECTCHOOSEN, CHOOSEN);
          }
          });
 
    
    d3.select("#topicsList").selectAll("li")
    .each(function(d, i){
          let element = $(this);
          if (currentTopicIds.indexOf(d.id) > -1){
            highlightTopicElement(element, DIRECTCHOOSEN, CHOOSEN);
          }
          });
    
    
    d3.select("#textsList").selectAll("li")
    .each(function(d, i){
          let element = $(this);
          if (currentTextIds.indexOf(d.id) > -1){
          highlightTextElement(element, DIRECTCHOOSEN, CHOOSEN);
          }
          });
    
    d3.select("#themesList").selectAll("li")
    .each(function(d, i){
          let element = $(this);
          if (currentThemeIds.indexOf(d.id) > -1){
          highlightThemeElement(element, DIRECTCHOOSEN, CHOOSEN);
          }
          });

    resetAllArgumentMarkings();
    
}


// Handles hovering for a document element
function onTextElementMouseEnter() {
    resetHighlight();
	highlightTextElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT);
}

// Handles hovering for a document element
function onTextElementMouseLeave() {
	resetHighlight();
}



// Handles hovering for a term element
function onTermElementMouseEnter() {
    resetHighlight();
	highlightTermElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT);
}

// Handles hovering for a term element
function onTermElementMouseLeave() {
	resetHighlight();
}

// Handles hovering for a topic element
function onTopicElementMouseEnter() {
    resetHighlight();
	highlightTopicElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT);
}

// Handles hovering for a topic element
function onTopicElementMouseLeave() {
	resetHighlight();
}

// Handles hovering for a theme element
function onThemeElementMouseEnter() {
    resetHighlight();
	highlightThemeElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT);
}

// Handles hovering for a theme element
function onThemeElementMouseLeave() {
	resetHighlight();
}

////
// Render link highlights
//////////

// Help function for rendering link highlighting
function renderLinksHighlight(name, link){
    d3.select(name).append("line")
    .classed("link-overlay-highlight-bg", true)
    .attr("x1", parseFloat(link.attr("x1")))
    .attr("y1", parseFloat(link.attr("y1")))
    .attr("x2", parseFloat(link.attr("x2")))
    .attr("y2", parseFloat(link.attr("y2")));
    
    d3.select(name).append("line")
    .classed("link-overlay-highlight", true)
    .attr("x1", parseFloat(link.attr("x1")))
    .attr("y1", parseFloat(link.attr("y1")))
    .attr("x2", parseFloat(link.attr("x2")))
    .attr("y2", parseFloat(link.attr("y2")));
    
}

// Renders highlighting for a term-to-topic link
function renderTermToTopicLinkHighlight() {
    var link = d3.select(this);
    renderLinksHighlight("#termLinksHighlight", link);
}

// Renders highlighting for a text-to-topic link
function renderTextToTopicLinkHighlight() {
    var link = d3.select(this);
    renderLinksHighlight("#topicTextLinksHighlight", link);
}

// Renders highlighting for a text-to-theme link
function renderTextToThemeLinkHighlight() {
    var link = d3.select(this);
    renderLinksHighlight("#themeLinksHighlight", link);
}

//////
// Functions for direct highligting
/////

// Highlights the given term element and related items
function highlightTermElement(termElement, direct, indirect) {
	
	// First of all, highlight the element under cursor
	termElement.addClass(direct);

    // Get the term datum
	let term = d3.select(termElement.get(0)).datum();
	
    highlightTermToTopicLink(term.term);
    highlightTermToTextLink(term.term);
    highlightTermToThemeLink(term.term);
    
    secondaryHighlightTopics(isAssociatedTermTopic, indirect, term.term);
    secondaryHighlightTexts(isAssociatedTextTerm, indirect, term.term);
    secondaryHighlightThemes(isAssociatedThemeTerm, indirect, term.term);
	
}

// Highlights the given topic element and related items
function highlightTopicElement(topicElement, direct, indirect) {

	// First of all, highlight the element under cursor
	topicElement.addClass(direct);
	
	// Get the topic datum
	let topic = d3.select(topicElement.get(0)).datum();
	
    // Perform secondary highlights
    secondaryHighlightTerms(isAssociatedTermTopic, indirect, topic.id);
    secondaryHighlightTexts(isAssociatedTextTopic, indirect, topic.id);
    secondaryHighlightThemes(isAssociatedThemeTopic, indirect, topic.id);

    highlightTopicToTermLink(topic.id);
    highlightTopicToTextLink(topic.id);
    highlightTopicToThemeLink(topic.id);
	}



// Highlights the given document element and related items
function highlightTextElement(textElement, direct, indirect) {
    // Get the document datum
    let text = d3.select(textElement.get(0)).datum();
    
    // First of all, highlight the element under cursor
    textElement.addClass(direct);
    
    if(direct == DIRECTCHOOSEN){
        showFullText(textElement);
    }
    
    //d3.select(textElement.get(0)).selectAll('.snippet-text').classed("textchosen", true);
    //d3.select(textElement.get(0)).selectAll('.full-text').classed("textchosen", true);
    //snippetText
    //let fullText = d3.select(textElement.selectAll("full-text"));
    
    //let fullText = d3.select(textElement.get(0)).selectAll('.full-text')
    //fullText.addClass(direct);
    
    // Highlight links
    highlightTopicsToTextLink(text.id);
    highlightTextToThemeLink(text.id);
    highlightTextToTermLink(text.id);
    
    // Get the related topics and mark their elements, as well as other related items
    secondaryHighlightTopics(isAssociatedTextTopic, indirect, text.id);
    secondaryHighlightThemes(isAssociatedThemeText, indirect, text.id);
    secondaryHighlightTerms(isAssociatedTermText, indirect, text.id);

}

function colorAllTagsWithTheSameColor(textElement){
       d3.select(textElement.get(0)).selectAll(".term-to-mark").classed("specifictermchosen", true);
}

function showFullText(textElement){
    d3.select(textElement.get(0)).selectAll('.text-container').classed("text-border", true);
    d3.select(textElement.get(0)).selectAll('.snippet-text').classed("not-displayed-text", true);
    d3.select(textElement.get(0)).selectAll('.full-text').classed("not-displayed-text", false);

    d3.select(textElement.get(0)).selectAll('.snippet-text').classed("displayed-text", false);
    d3.select(textElement.get(0)).selectAll('.full-text').classed("displayed-text", true);

    
    let textId = d3.select(textElement.get(0)).datum().id;
    
    // if current text is selected
    if (currentTextIds.indexOf(textId) > -1){
        colorAllTagsWithTheSameColor(textElement);
    }
}

function secondaryHighlightTermsInText(textElement){
    let textId = d3.select(textElement.get(0)).datum().id;
    
  
    // If topics are chosen, hightlight terms that belong to thees topics, and in accordance to the strength of these terms to these topics
    d3.select(textElement.get(0)).selectAll(".term-to-mark").classed("specifictermchosen", false);
    if (modelTopics != []){
        for (let i = 0; i < modelTopics.length; i++) {
            let topic = modelTopics[i]["id"];
            // If topic is selected
            if (currentTopicIds.indexOf(topic) > -1){
                d3.selectAll('.topic_' + topic).classed("termintextnotchosen", false);
            }
            else{
                d3.selectAll('.topic_' + topic).classed("termintextnotchosen", true);
            }
        }
    }

    // If terms are chosen, highlight these terms
    if (currentTermIds.length > 0){
        // Default is that nothing is marked
        d3.select(textElement.get(0)).selectAll(".term-to-mark").classed("specifictermchosen", false);
        // Select the terms that are to be marked
        d3.select(textElement.get(0)).selectAll(".term-to-mark").each(function(d, i) {
                                                                            let foundterm = $(this).html().trim().toLowerCase();
                                                                            if (splittedTerms.indexOf(foundterm) >= 0){
                                                                            d3.select($(this).get(0)).classed("specifictermchosen", true);
                                                                            }});
    }
}

// Highlights the given theme element and related items
function highlightThemeElement(themeElement, direct, indirect) {
	
	// First of all, highlight the element under cursor
	themeElement.addClass(direct);
	
	// Get the theme datum
	let theme = d3.select(themeElement.get(0)).datum();
    
    // Render secondary highligh and links
    secondaryHighlightTopics(isAssociatedThemeTopic, indirect, theme.id);
    secondaryHighlightTexts(isAssociatedTextTheme, indirect, theme.id);
    secondaryHighlightTerms(isAssociatedTermTheme, indirect, theme.id);
    
    highlightThemeToTextLink(theme.id);
    highlightThemeToTopicLink(theme.id);
    highlightThemeToTermLink(theme.id);
}


////////////////
// For performing secondary highlighting
//////

function secondaryHighlightTopics(associationMethod, highlightClass, key){
    d3.select("#topicsList").selectAll("li")
    .filter(function(d, i){
            return associationMethod(key, d.id) && currentTopicIds.indexOf(d.id) == -1;
            })
    .classed(highlightClass, true);
}

// note the different order of the arguments to the associationMethod compared to secondaryHighlightTopics

function secondaryHighlightTerms(associationMethod, highlightClass, key){
    d3.select("#termsList").selectAll("li")
    .filter(function(d, i){
            return associationMethod(d.term, key) && currentTermIds.indexOf(d.term) == -1;
            })
    .classed(highlightClass, true);
    //.each(highlightTermToTopicLinks);
    
    
}

// note the different order of the arguments to the associationMethod compared to secondaryHighlightTopics
function secondaryHighlightTexts(associationMethod, highlightClass, key){
    d3.select("#textsList").selectAll("li")
    .filter(function(d, i){
            return associationMethod(d.id, key) && currentTextIds.indexOf(d.id) == -1;
            })
    .classed(highlightClass, true)
    .each(function(d, i){
          if (highlightClass == CHOOSEN){
          secondaryHighlightTermsInText($(this));
        }
          });
}



// note the different order of the arguments to the associationMethod compared to secondaryHighlightTopics
function secondaryHighlightThemes(associationMethod, highlightClass, key){
    d3.select("#themesList").selectAll("li")
    .filter(function(d, i){
            return associationMethod(d.id, key) && currentThemeIds.indexOf(d.id) == -1;
            })
    .classed(highlightClass, true);
}

///////
// Higlight links
//////

function highlightTopicsToTextLink(topicId){
    // Get the related topic-to-theme links and mark them
    d3.selectAll(".topics-to-texts")
    .filter(function(f, j){
            return topicId == f.document;
            })
    .classed("link-highlight", true)
    .each(renderTextToTopicLinkHighlight);
}

function highlightTextToThemeLink(textId){
    // Get the related topic-to-theme links and mark them
    d3.selectAll(".texts-to-themes")
    .filter(function(f, j){
            return textId == f.text;
            })
    .classed("link-highlight", true)
    .each(renderTextToThemeLinkHighlight);
}

function highlightThemeToTextLink(themeId){
    // Get the related topic-to-theme links and mark them
    d3.selectAll(".texts-to-themes")
    .filter(function(f, j){
            return themeId == f.theme;
            })
    .classed("link-highlight", true)
    .each(renderTextToThemeLinkHighlight);
}


function highlightTermToTopicLink(termName){
    // Get the related term-to-topic links and mark them
    d3.selectAll(".terms-to-topics")
    .filter(function(f, i){
            return termName == f.term;
            })
    .classed("link-highlight", true)
    .each(renderTermToTopicLinkHighlight);

}

/////
function highlightTopicToTermLink(topicId){
    // Get the related term-to-topic links and mark them
    d3.selectAll(".terms-to-topics")
    .filter(function(d, i){
            return d.topic == topicId;
            })
    .classed("link-highlight", true)
    .each(renderTermToTopicLinkHighlight);
}

function highlightTopicToTextLink(topicId){
    // Get the related term-to-topic links and mark them
    d3.selectAll(".topics-to-texts")
    .filter(function(d, i){
            return d.topic == topicId;
            })
    .classed("link-highlight", true)
    .each(renderTextToTopicLinkHighlight);
}

function highlightTopicToThemeLink(topicId){
    // Get the related term-to-topic links and mark them
    d3.selectAll(".texts-to-themes")
    .filter(function(d, i){
            return isAssociatedTextTopic(d.text, topicId);
            })
    .classed("link-highlight", true)
    .each(renderTextToThemeLinkHighlight);
}

function highlightThemeToTopicLink(themeId){
    // Get the related term-to-topic links and mark them
    d3.selectAll(".topics-to-texts")
    .filter(function(d, i){
            return isAssociatedThemeTopic(themeId, d.topic);
            })
    .classed("link-highlight", true)
    .each(renderTextToTopicLinkHighlight);
}

function highlightTextToTermLink(textId){
    // Get the related term-to-topic links and mark them
    d3.selectAll(".terms-to-topics")
    .filter(function(d, i){
            return (isAssociatedTextTopic(textId, d.topic) &&
                    isAssociatedTextTerm(textId, d.term));
            })
    .classed("link-highlight", true)
    .each(renderTermToTopicLinkHighlight);
}

function highlightTermToTextLink(termName){
    // Get the related term-to-topic links and mark them
    d3.selectAll(".topics-to-texts")
    .filter(function(d, i){
            return (isAssociatedTextTerm(d.document, termName) &&
                    isAssociatedTermTopic(termName, d.topic))
            })
    .classed("link-highlight", true)
    .each(renderTextToTopicLinkHighlight);
}

function highlightTermToThemeLink(termName){
    // Get the related text-to-theme links and mark them
    d3.selectAll(".texts-to-themes")
    .filter(function(d, i){
            return (isAssociatedTextTerm(d.text, termName) &&
                     isAssociatedTextTheme(d.text, d.theme));
            })
    .classed("link-highlight", true)
    .each(renderTextToThemeLinkHighlight);
}

function highlightThemeToTermLink(themeId){
    // Get the related term-to-topic links and mark them
    d3.selectAll(".terms-to-topics")
    .filter(function(d, i){
            return (isAssociatedThemeTerm(themeId, d.term) &&
                    isAssociatedThemeTopic(themeId, d.topic));
            })
    .classed("link-highlight", true)
    .each(renderTermToTopicLinkHighlight);
}

/////
/// Document searches
/////
// TODO: right now, the functions below are basically copy-pasted for other lists (terms, topics, themes)
// They are actually almost identical except for the input field / button IDs and textual attribute of the model
// This should be refactored in the future...

// Handles the document search update
function onTextSearch(){
	textSearchText = $("#textSearch").val();
	filterDisplayedDocuments();
}


// Filters the displayed document elements
function filterDisplayedDocuments() {
	let query = textSearchText ? textSearchText.toLowerCase().trim() : null;
	
	d3.select("#textsList").selectAll("li")
	.classed("not-displayed", function(d, i){
		if (!query)
			return false;
		return (!d.marked_text_tok || d.marked_text_tok.toLowerCase().indexOf(query) < 0);
	});
	
	renderLinks();
}


/*
// Filters the displayed document elements
function filterDisplayedDocuments() {
    resetSelectedDataExcept();
    let query = textSearchText ? textSearchText.toLowerCase().trim() : null;
    
    d3.select("#textsList").selectAll("li")
    .each(function(d, i){
             if (!query)
                return false;
             if (d.text.toLowerCase().indexOf(query.toLowerCase()) > 0){
          
                toggleChosenElement(d.id, modelToggleTextElement);
                renderLinks();
                if (currentTextIds.indexOf(d.id) > -1){ // if chosen
                    highlightTextElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT);
                }
          
                //currentTextIds.push(d.id);
             }});
}*/


/////
/// Term searches
/////

// Handles the term search update
function onTermSearch(){
	termSearchText = $("#termSearch").val();
	filterDisplayedTerms();
}


// Filters the displayed term elements
function filterDisplayedTerms() {
	let query = termSearchText ? termSearchText.toLowerCase().trim() : null;
	
	d3.select("#termsList").selectAll("li")
	.classed("not-displayed", function(d, i){
		if (!query)
			return false;
		
		return (!d.term || d.term.toLowerCase().indexOf(query) < 0);
	});
	
	resetHighlight();
	renderLinks();
}

/////
/// Topic searches
/////

// Handles the topic search update
function onTopicSearch(){
	topicSearchText = $("#topicSearch").val();
	filterDisplayedTopics();
}



// Filters the displayed topic elements
function filterDisplayedTopics() {
	let query = topicSearchText ? topicSearchText.toLowerCase().trim() : null;
	
	d3.select("#topicsList").selectAll("li")
	.classed("not-displayed", function(d, i){
		if (!query)
			return false;
		
        let userDefinedName = modelGetTopicNameForId(d.id);

        if (userDefinedName == undefined) {
             return (!d.defaultlabel || d.defaultlabel.toLowerCase().indexOf(query) < 0);
        }
             // else
        return (userDefinedName.toLowerCase().indexOf(query) < 0);
             
	});
	
	resetHighlight();
	renderLinks();
}


/////
/// Theme searches
/////

// Handles the theme search update
function onThemeSearch(){
	themeSearchText = $("#themeSearch").val();
	filterDisplayedThemes();
}



// Filters the displayed theme elements
function filterDisplayedThemes() {
	let query = themeSearchText ? themeSearchText.toLowerCase().trim() : null;
	
	d3.select("#themesList").selectAll("li")
	.classed("not-displayed", function(d, i){
		if (!query)
			return false;
		
		return (!d.label || d.label.toLowerCase().indexOf(query) < 0);
	});
	
	resetHighlight();
	renderLinks();
}


////////
// Hide ans show search buttons
////////

// All fields
function hideSearchFields(){
    let field_names = ["#termSearch", "#termSearchClear", "#topicSearch", "#topicSearchClear", "#textSearch", "#textSearchClear", "#themeSearch", "#themeSearchClear"];
    for (let i = 0; i < field_names.length; i++){
        d3.select(field_names[i]).classed("search-input_hidden", true);
    }
}

// Help functions
function showSearchField(fieldName, clearName, showFieldClass){
    d3.select(fieldName).style("visibility", "visible");
    d3.select(fieldName).classed(showFieldClass, true)
    d3.select(clearName).style("visibility", "visible");
    d3.select(fieldName).each(function(){
                              $(this).focus()
                              })
}

function hideSearchField(fieldName, clearName, showFieldClass){
    d3.select(fieldName).style("visibility", "hidden");
    d3.select(fieldName).classed(showFieldClass, false)
    d3.select(clearName).style("visibility", "hidden");
}

// Terms
function onTermSearchButtonClick(){
    showSearchField("#termSearch", "#termSearchClear", "search-input_terms");
}

function onTermSearchClear(){
    $("#termSearch").val("");
    $("#termSearch").trigger("keyup");
    hideSearchField("#termSearch", "#termSearchClear", "search-input_terms");
}

// Topics
function onTopicSearchButtonClick(){
    showSearchField("#topicSearch", "#topicSearchClear", "search-input_topics");
}

function onTopicSearchClear(){
    $("#topicSearch").val("");
    $("#topicSearch").trigger("keyup");
    hideSearchField("#topicSearch", "#topicSearchClear", "search-input_topics");
}

// Texts
function onTextSearchButtonClick(){
    showSearchField("#textSearch", "#textSearchClear", "search-input-text");
}

// Handles the document search update
function onTextSearchClear(){
    $("#textSearch").val("");
    $("#textSearch").trigger("keyup");
    hideSearchField("#textSearch", "#textSearchClear", "search-input-text");
}

// Themes
function onThemeSearchButtonClick(){
    showSearchField("#themeSearch", "#themeSearchClear", "search-input-themes");
}

// Handles the theme search update
function onThemeSearchClear(){
    $("#themeSearch").val("");
    $("#themeSearch").trigger("keyup");
    hideSearchField("#themeSearch", "#themeSearchClear", "search-input-themes");
}

// TODO: Now labels are hidden and shown in javascript. If this gets too slow (as the themes need to be re-populated)
// use visibility in css instead
function onShowLabels(){
    if (showLabels){
        showLabels = false;
        $("#showLabels").removeClass("button-active");
        
    }
    else{
        showLabels = true;
        $("#showLabels").addClass("button-active");
    }
    controllerDoPopulateThemes(true);
}

function onLockThemesSorting(){
    if (!doThemesSorting){
        doThemesSorting = true;
	$("#doThemeSorting").addClass("button-active");
        modelSortThemesWithMachineLearningIfTextChosen();
        
    }
    else{
        doThemesSorting = false;
        modelResetRecentlyClickedForMachineLearningSorting();
        $("#doThemeSorting").removeClass("button-active");
        modelSortThemesWithMachineLearningIfTextChosen();
    }
}


function onLockTextSorting(){
    if (lockTextsSorting){
        lockTextsSorting = false;
        $("#lockTextSorting").removeClass("button-active");
	doResetHighlightAfterStateChange();
    }
    else{
        lockTextsSorting = true;
        $("#lockTextSorting").addClass("button-active");
    }
}

function onLockTermsSorting(){
    if (lockTermsSorting){
        lockTermsSorting = false;
        $("#lockTermsSorting").removeClass("button-active");
	doResetHighlightAfterStateChange();
    }
    else{
        lockTermsSorting = true;
        $("#lockTermsSorting").addClass("button-active");
    }
}


function onLockTopicsSorting(){
    if (lockTopicsSorting){
        lockTopicsSorting = false;
        $("#lockTopicsSorting").removeClass("button-active");
	doResetHighlightAfterStateChange();
    }
    else{
        lockTopicsSorting = true;
        $("#lockTopicsSorting").addClass("button-active");
    }
}


/*******************/

/* Extra functions for Tag der Wissenschaften */
var showSentiment = false;
var showClaim = false;
var showSupporting = false;
var showOpposing = false;

// Start by hiding the argumentation-specific buttons, and then show them if the model has the configuration that these
// buttons are to be shown

$("#sentiment").click(onShowSentiment);
$("#claim").click(onShowClaim);
$("#supporting").click(onShowSupporting);
$("#opposing").click(onShowOpposing);

d3.select("#sentiment").style("visibility", "hidden");
d3.select("#claim").style("visibility", "hidden");
d3.select("#supporting").style("visibility", "hidden");
d3.select("#opposing").style("visibility", "hidden");

function adaptArgumentationButtonsToModel(){

    showSentiment = false;
    showClaim = false;
    showSupporting = false;
    showOpposing = false;

    // Button for showing positive markers
    if (modelShowArgumentation == undefined){
	d3.select("#claim").style("visibility", "hidden");
	d3.select("#supporting").style("visibility", "hidden");
	d3.select("#opposing").style("visibility", "hidden");
    }
    else{
	d3.select("#claim").style("visibility", "visible");
	d3.select("#supporting").style("visibility", "visible");
	d3.select("#opposing").style("visibility", "visible");
    }
    if (modelShowSentiment == undefined){
	d3.select("#sentiment").style("visibility", "hidden");
    }
    else{
	d3.select("#sentiment").style("visibility", "visible");
    }
}

function resetAllArgumentMarkings(){
    showSentiment = false;
    showClaim = false;
    showSupporting = false;
    showOpposing = false;
    
    $("#sentiment").removeClass("sentiment-marker");
    d3.select("#textsList").selectAll("positive").each(function(){$(this).removeClass("positive-marker");})
    d3.select("#textsList").selectAll("negative").each(function(){$(this).removeClass("negative-marker");})
    d3.select("#textsList").selectAll("modifier").each(function(){$(this).removeClass("modifier-marker");})

    $("#claim").removeClass("claim");
    d3.select("#textsList").selectAll("claim").each(function(){$(this).removeClass("claim");})

    $("#supporting").removeClass("supporting");
    d3.select("#textsList").selectAll("support").each(function(){$(this).removeClass("supporting");})

    $("#opposing").removeClass("opposing");
    d3.select("#textsList").selectAll("oppose").each(function(){$(this).removeClass("opposing");})
    
}

function resetIfNoArgumentsAreChosen(){
    if (showSentiment == false && showClaim == false && showSupporting == false && showOpposing == false){
	addChoiceBasedHighlight();
    }
}

function onShowSentiment(){
    if (showSentiment){
        showSentiment = false;
        $("#sentiment").removeClass("sentiment-marker");
	d3.select("#textsList").selectAll("positive").each(function(){$(this).removeClass("positive-marker");})
	d3.select("#textsList").selectAll("negative").each(function(){$(this).removeClass("negative-marker");})
	d3.select("#textsList").selectAll("modifier").each(function(){$(this).removeClass("modifier-marker");})
	resetIfNoArgumentsAreChosen();
    }
    else{
	d3.select("#textsList").selectAll("positive").each(function(){$(this).addClass("positive-marker");})
	d3.select("#textsList").selectAll("negative").each(function(){$(this).addClass("negative-marker");})
	d3.select("#textsList").selectAll("modifier").each(function(){$(this).addClass("modifier-marker");})
        showSentiment = true;
        $("#sentiment").addClass("sentiment-marker");
	d3.selectAll(".term-to-mark").classed("termintextnotchosen", true);
	d3.selectAll(".term-to-mark").classed("specifictermchosen", false);
    }
}


function onShowClaim(){
    if (showClaim){
        showClaim = false;
        $("#claim").removeClass("claim");
	d3.select("#textsList").selectAll("claim").each(function(){$(this).removeClass("claim");})
	resetIfNoArgumentsAreChosen();
    }
    else{
	d3.select("#textsList").selectAll("claim").each(function(){$(this).addClass("claim");})
        showClaim = true;
        $("#claim").addClass("claim");
	d3.selectAll(".term-to-mark").classed("termintextnotchosen", true);
	d3.selectAll(".term-to-mark").classed("specifictermchosen", false);
    }
}



function onShowSupporting(){
    if (showSupporting){
        showSupporting = false;
        $("#supporting").removeClass("supporting");
	d3.select("#textsList").selectAll("support").each(function(){$(this).removeClass("supporting");})
	resetIfNoArgumentsAreChosen();
    }
    else{
	d3.select("#textsList").selectAll("support").each(function(){$(this).addClass("supporting");})
        showSupporting = true;
        $("#supporting").addClass("supporting");
	d3.selectAll(".term-to-mark").classed("termintextnotchosen", true);
	d3.selectAll(".term-to-mark").classed("specifictermchosen", false);
    }
}


function onShowOpposing(){
    if (showOpposing){
        showOpposing = false;
        $("#opposing").removeClass("opposing");
	d3.select("#textsList").selectAll("oppose").each(function(){$(this).removeClass("opposing");})
	resetIfNoArgumentsAreChosen();
    }
    else{
	d3.select("#textsList").selectAll("oppose").each(function(){$(this).addClass("opposing");})
        showOpposing = true;
        $("#opposing").addClass("opposing");
	d3.selectAll(".term-to-mark").classed("termintextnotchosen", true);
	d3.selectAll(".term-to-mark").classed("specifictermchosen", false);
    }
}


