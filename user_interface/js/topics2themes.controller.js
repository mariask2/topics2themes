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

var termsSmall = false;
var showLabels = true;
var doThemesSorting = true;
var lockTextsSorting = false;
var lockTermsSorting = false;
var lockTopicsSorting = false;
var showFullText = false;


// Holds terms selected, splitted for "/" and "_" into different terms
var splittedTerms = [];

/// Sort functions
/////////////////////


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
    "score/asc": sortTextScoreAsc,
    "themes/desc": sortTextThemesDesc,
    "themes/acs": sortTextThemesAsc,
    "label/desc": sortTextLabelDesc,
    "label/acs": sortTextLabelAsc,
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

var buffer = [];
var lastKeyTime = Date.now();



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

    document.addEventListener('keydown', onKeyDown);

    // Handlers for selecting and/or constructing data sets, models and analysis 
    $("#dataset").on("change", onDatasetChange);
    $("#newModel").on("click", onConstructNewModel);
    $("#modelVersion").on("change", onModelVersionListChange);
    $("#newAnalysis").on("click", onNewAnalysis);
    $("#analysisVersion").on("change", onAnalysisVersionListChange);
    $("#exportAnalysis").on("click", onExportAnalysis);

    // Search buttons
    $("#termSearchButton").on("click", onTermSearchButtonClick);
    $("#topicSearchButton").on("click", onTopicSearchButtonClick);
    $("#textSearchButton").on("click", onTextSearchButtonClick);
    $("#themeSearchButton").on("click", onThemeSearchButtonClick);
                  
                  
	$("#termsList, #topicsList, #themesList, #textsList").on("scroll", onListScroll);
	
	
	$("#termSearchClear").on("click", onTermSearchClear);
	$("#termSearch").on("keyup", onTermSearch);
	$("#topicSearchClear").on("click", onTopicSearchClear);
	$("#topicSearch").on("keyup", onTopicSearch);
	$("#textSearchClear").on("click", onTextSearchClear);
	$("#textSearch").on("keyup", onTextSearch);
	$("#themeSearchClear").on("click", onThemeSearchClear);
	$("#themeSearch").on("keyup", onThemeSearch);
	
	
	$("#topicsList").on("change", ".topic-element .title-label", onTopicRename);
    $("#newTheme").on("click", onThemeAdd);
	$("#themesList").on("change", ".theme-element .title-label", onThemeRename);
    $("#textsList").on("click", ".text-element .change-label-trigger", onChooseLabelClick);
    $("#textsList").on("click", ".text-element .theme-text-remove-button", onThemeTextRemoveAtTextElement);
	$("#themesList").on("click", ".theme-element .theme-remove-button", onThemeRemove);
	
	$(".sort-terms-trigger").on("click", onSortTermsList);
	$(".sort-topics-trigger").on("click", onSortTopicsList);
	$(".sort-documents-trigger").on("click", onSortDocumentsList);
    $(".sort-themes-trigger").on("click", onSortThemesList);
                  
	// list click events to select a items as active
    $("#termsList").on("click", ".term-element", onTermElementClick);
    $("#topicsList").on("click", ".topic-element", onTopicElementClick);
    $("#textsList").on("click", ".text-element", onTextElementClick);
    $("#themesList").on("click", ".theme-element", onThemeElementClick);

    $("#textsList").on("mouseup", ".jp_lemma", onSelectionChange);

    

    // Button for showing full text
    $("#showFullText").on("click", onShowFullText);

    // Button for resizing terms panel
    $("#resizeTerms").on("click", onResizeTerms);

    // Button for hide and show labels on themes
    $("#showLabels").on("click", onShowLabels);
                  
    // Button for lock and unlock the sorting of themes
    $("#doThemeSorting").on("click", onDoThemeSorting);

    // Button for lock and unlock the sorting of texts
    $("#lockTextSorting").on("click", onLockTextSorting);

    // Button for lock and unlock the sorting of terms
    $("#lockTermsSorting").on("click", onLockTermsSorting);

      // Button for lock and unlock the sorting of terms
    $("#lockTopicsSorting").on("click", onLockTopicsSorting);

             
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
    let key = localStorage.getItem('topics2themes-authkey');
    if (key === null) {
	key = prompt("Please enter authentication key");
    }
   
    if (key !== null && key.trim() != ""){
        authenticationKey = key
	localStorage.setItem('topics2themes-authkey', key);
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
    
    d3.select("#topicsList").selectAll("li").selectAll("textarea")
	.property("disabled", true);
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

    d3.select("#topicsList").selectAll("li").selectAll("textarea")
	.property("disabled", false);
}


///////
// Resize
///////

// Handles window resize
$(window).on('resize', function() {
    if(this.resizeTO) clearTimeout(this.resizeTO);
    this.resizeTO = setTimeout(function() {
        $(this).trigger("resizeEnd");
    }, 500);
});

$(window).on("resizeEnd", function(){
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
    setTimeout(renderLinks, 0);
});

// Resizes the containers based on the current window size
function resizeContainers() {
	var otherHeight = 0;
	$(".outer-element").each(function(){
		otherHeight += $(this).outerHeight(true);
	})
		
	// Several magic numbers below to account for heights of headers, spaces, etc.
	var maxAvailableHeight = windowHeight - otherHeight
		- parseInt($("body > div.page-wrapper").css("margin-top")) - parseInt($("body > div.page-wrapper").css("border-top-width"));
	var mainAvailableHeight = maxAvailableHeight;
	
	// Adjust the sizes of the inner containers
	var innerAvailableHeight = mainAvailableHeight - TOP_OFFSET;
	$("#termsList, #topicsList, #themesList, #textsList").css("max-height", innerAvailableHeight + "px");
    
}



///////////////
/// For the panel above with datasets, models and analyses versions
///////////////

// Data set changes
//////

async function populateDataChoices(){
    let choices = await modelGetDataSetChoices();

    $("#dataset").empty();
    
    // Append the terms
    d3.select("#dataset").selectAll("option")
	.data(choices)
	.enter()
	.append("option")
	.property("selected", (d) => d.value == SELECTDATASETTEXT)
	.property("disabled", (d) => d.value == SELECTDATASETTEXT)
	.attr("value", (d) => d.value)
	.text((d) => d.value);
}


async function onDatasetChange() {
    var newDataset = $("#dataset").val();
    
    if (newDataset == modelCurrentDataset)
        return;
    
    resetInterface();
    disableAnalysisChoices();
    disableThemeButtons();
    await modelLoadModelForSelectedDataSet(newDataset);
    controllerDoPopulateInterface();
    controllerDoPopulateModelChoices(modelModelsForCurrentDataset);
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
	    .attr("id", (d) => d.id)
	    .property("selected", (d) => d.value == SELECTMODELTEXT)
	    .property("disabled", (d) => d.value == SELECTMODELTEXT)
	    .attr("value", (d) => d.value)
	    .text((d) => d.value);
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

async function onModelVersionListChange(element) {
    var newModelVersionId  = $("#modelVersion").children('option:selected').attr("id");
    
    if (newModelVersionId == modelCurrentModelId)
        return;
    
    resetInterface();
    disableThemeButtons();
    let path1 = (async () => {
	await modelInitializeData(newModelVersionId);
	controllerDoPopulateInterface();
    })();
    let path2 = (async () => {
	await modelLoadAnalysesForSelectedModel(newModelVersionId);
	controllerDoPopulateAnalysisChoices(modelAnalysesForCurrentModel);
    })();
    await Promise.all([path1, path2]);
}

/// Selection of analyses
async function onAnalysisVersionListChange(element) {
    
    var newAnalysisVersionId  = $("#analysisVersion").children('option:selected').attr("id");
    
    if (newAnalysisVersionId == modelCurrentAnalysisVersionId)
        return;
    
    await modelLoadNewAnalysis(newAnalysisVersionId);
    controllerDoPopulateTopicElements();
    controllerDoPopulateThemes();
    // TODO: Perhaps possible to save time by only population text elements controllerDoPopulateTextElements();
    setTimeout(controllerDoPopulateInterface, 0);
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
	    .attr("id", (d) => d.id)
	    .property("selected", (d) => d.value == SELECTANALYSISTEXT)
	    .property("disabled", (d) => d.value == SELECTANALYSISTEXT)
	    .attr("value", (d) => d.value)
	    .text((d) => d.value);
    }
    else{
        $("#analysisVersion").addClass("disabled");
        $("#analysisVersion").attr("disabled", true);

	$("#newAnalysis").removeClass("disabled");
	$("#newAnalysis").attr("disabled", false);
    }
}


function onNewAnalysis(){
    var analysisName = prompt("Please enter the name of the analysis to create");

    if (analysisName == null || analysisName == "") {
        alert("No new analysis created, a name must be given");
    } else {
	disableAnalysisChoices();
	(async () => {
	    let modelCurrentAnalysisName = await modelConstructNewAnalysis(analysisName);
	    controllerDoPopulateAnalysisChoices(modelAnalysesForCurrentModel);
	    controllerSelectChosenAnalysis(modelCurrentAnalysisName);
	})();
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
	.classed("term-element", true)
	.style("padding", "5px 7px")
	.append("span")
	.classed("title-label", true)
	.text((d) => d.term.replace(/_/g, " "));
    
    // topics
    // only populate topics if no analysis is chosen. If an analysis is chosen, this will instead be performed in from the callback when loading an analysis version
    if (modelCurrentAnalysisVersionId == null){

        controllerDoPopulateTopicElements();
        disableThemeButtons(); // To disable the text areas of the topics, as they should be be changed when no theme is chosen
    }
    

    //texts
    controllerDoPopulateTextElements();

    // Themes are populated in  controllerDoPopulateThemes, when an analysis version is selected, and not here
//    controllerRepopulateTheme(); // TODO: To make sure texts with changed labels are propagated to themes, is this still a problem?
    
    
    adaptArgumentationButtonsToModel();
   
    
    // Sort the lists initially
    doDefaultSort();
    
    // Resize the containers
    resizeContainers();

    // Disable term highlighting that are not to be there
    resetHighlight();
    
    // Draw the links over an SVG canvas
    setTimeout(renderLinks, 0);
    

}

function controllerDoPopulateTextElements(){
    $("#textsList").empty();
    let textElementSelection = d3.select("#textsList").selectAll("li")
	.data(modelDocuments)
	.enter()
	.append("li");
    //.attr("draggable", true)
    populateTextElement(textElementSelection);
}

function doReplaceChildren(node, elements) {
    for (const element of elements) {
	node.appendChild(element);
    }
}

d3.selection.prototype.replaceChildren = function (elements) {
    this.selectAll('*').remove();
    if (typeof elements === "function") {
	this.each(function (d, i) {
	    let result = elements.apply(this, [d, i]);
	    doReplaceChildren(this, result);
	});
    } else {
	doReplaceChildren(this.node(), elements);
    }
    return this;
};

// For updating the label in one specific text element
function controllerDoPopulateOneTextElement(data){
    let container = d3.select("#textsList").selectAll("li")
	.filter(function(f, j){
            return data.text_id == f.id;
        })
	.selectAll(".label-button-container");
    populateTextElementLabel(container);
}


function controllerDoPopulateTopicElements(){
    $("#topicsList").empty();
    // Append the topics
    d3.select("#topicsList").selectAll("li")
	.data(modelTopics)
	.enter()
	.append("li")
	.classed("topic-element", true)
	.append("textarea")
	.attr("type", "text")
	.classed("title-label", true)
	.classed("topic-input", true)
	.attr("placeholder", (d) => "Topic #" + d.id)
	.property("value", (d) => modelGetTopicNameForId(d.id) || d.defaultlabel)
}


async function onChooseLabelClick(event){
    let element = $(this);
    let userDefinedLabel = element.attr("id");
    let textId = element.attr("text-id");
    let data = await modelDefineUserLabel(textId, userDefinedLabel);
    controllerDoPopulateOneTextElement(data);
    controllerRepopulateTheme();
}

function populateTextElement(textElementSelection){
    textElementSelection.selectAll('*').remove(); // As this function is also used for repopulation, start with emptying what is there
    textElementSelection = textElementSelection
	.classed("text-element", true);
    let textContainer = textElementSelection.append("p");
    textContainer.classed("text-container", true);
    let labelButtonContainer = textContainer
	.append("span")
	.classed("label-button-container", true)
	.attr("draggable", true)
    populateTextElementLabel(labelButtonContainer);
    textContainer
	.append("div")
	.classed("full-text", true)
	.classed("text-label", true)
	.classed("not-displayed-text", !showFullText)
	.classed("displayed-text", showFullText)
	.html((d) => d.marked_text_tok);
    textContainer
	.append("div")
	.classed("snippet-text", true)
	.classed("text-label", true)
	.classed("not-displayed-text", showFullText)
	.classed("displayed-text", !showFullText)
	.html((d) => d.snippet);

    // Add additional labels
    textElementSelection
	.append("div")
	.classed("texts-info-container", true)
	.selectAll("span")
	.data((d) => d.additional_labels)
	.enter()
	.append("span")
	.classed("label", true)
	.classed("additional-label-badge", true)
	.text((d) => d)

    // Add the info about the links between the text and the theme
    textElementSelection
	.append("div")
	.classed("theme-texts-container", true)
	.selectAll("span")
	.data((d) => modelThemes.filter(theme => isAssociatedThemeText(theme.id, d.id)).map(theme => ({theme, d})))
	.enter()
	.append("span")
	.classed("theme-texts-label", true)
	.text((d) => "Theme #" + d.theme.id + "\u00a0")
	.classed("theme-indicator", true)
	.each(function (d) {
	    $(this).data("themeid", d.theme.id);
	    $(this).data("textid", d.d.id);
	})
	.append("button")
	.attr("type", "button")
	.classed("theme-text-remove-button", true)
	.attr("aria-label", "Remove text from theme")
	.attr("title", "Remove text from theme")
	.append("span")
	.classed("glyphicon", true)
	.classed("glyphicon-remove", true)
	.classed("text-theme-remove-glyph", true)
	.attr("aria-hidden", "true")

    textElementSelection.selectAll(".term-to-mark").classed("specifictermchosen", true);
}

function populateTextElementLabel(containerSelection){
    containerSelection.selectAll('*').remove();
    let buttonGroup = containerSelection
	.append("div")
	.classed("labelbuttons", true);
    if (modelCurrentAnalysisVersionId != null){
	let button = buttonGroup
	    .append("span")
            .classed("popupmenu", true)
	    .on("click", function () { return popupmenuclick.call(this, d3.event) })
            .attr("aria-haspopup", "true")
            .attr("aria-expanded", "false")
	addBadgeLabel(button, (d) => modelGetTextLabelForId(d.id) || d.label)
            .classed("badge-main-label", true)
            .classed("choose-label-trigger", true)
            .classed("badge-main-label-user-chosen", (d) => modelGetTextLabelForId(d.id) != undefined)
	    .append("span")
            .classed("glyphicon", true)
            .classed("glyphicon-sort-by-attributes", true)
            .classed("choose-label-trigger", true)
            .classed("choose-label-glyphicon", true)
	let popupmenu = buttonGroup
	    .append("ul")
	    .classed("choose-label-trigger", true)
	    .classed("popupmenu-body", true)
	for (const category of modelLabelCategories){
	    addBadgeLabel(popupmenu, (d) => category["label"])
		.attr("text-id", (d) => d.id)
		.classed("choose-label-trigger", true)
		.classed("change-label-trigger", true)
	    popupmenu
		.append("span")
		.classed("choose-label-trigger", true)
	}
    } else {
	addBadgeLabel(buttonGroup)
	    .classed("badge-main-label", true)
    }
}

function addBadgeLabel(selection, labelFunction) {
    if (labelFunction === undefined) {
	labelFunction = (d) => d.label;
    }
    return selection
	.append("span")
	.style("background-color", (d) => modelCategoryToColor[labelFunction(d)])
	.classed("label", true)
	.classed("text-badge", true)
	.attr("id", (d) => labelFunction(d))
	.text((d) => labelFunction(d).length == 1 ? labelFunction(d) + " " : labelFunction(d))
}

// Populates a theme element
function populateThemeElements(themesList) {
    themesList.selectAll('*').remove();
    themesList = themesList.classed("theme-element", true);
    themesList
	.append("button")
	.attr("type", "button")
	.classed("theme-remove-button", true)
	.attr("aria-label", "Remove theme without associated texts")
	.attr("title", "Remove theme without associated texts")
	.classed("disabled", d => hasThemeAssociatedTexts(d.id))
	.append("span")
	.classed("glyphicon", true)
	.classed("glyphicon-remove", true)
	.attr("aria-hidden", "true")
    themesList
	.append("span")
	.classed("index-label", true)
	.text(d => "Theme #" + d.id)
    themesList
	.append("textarea")
	.attr("type", "text")
	.classed("title-label", true)
	.attr("placeholder", d => "Theme #" + d.id + " (click to add description)")
	.property("value", d => d.label);
    let themeTexts = themesList
	.append("div")
	.classed("theme-texts-container", true)
    if(showLabels){
	let badges = themeTexts
	    .selectAll("div.themes-label-container")
	    .data(d => getBadges(d))
	    .enter()
	    .append("div")
	    .classed("themes-label-container", true)
	    .selectAll("span")
	    .data(d => d)
	    .enter()
	addBadgeLabel(badges, (d) => d.label)
	themeTexts
	    .append("div")
	    .classed("themes-additiona-label-container", true)
	    .selectAll("span")
	    .data(d => getAdditionalLabels(d))
	    .enter()
	    .append("span")
	    .classed("label", true)
	    .classed("additional-label-badge", true)
	    .text(d => d.label + " (" + d.count + ")")
    }
}

function getBadges(d) {
    let themeId = d.id
    let theme = modelThemesToTexts[themeId];
    if (theme === undefined) {
	return []
    }
    let badges = getBadgesCounter(theme);
    return modelLabelCategories.map(c => _.times(badges[c.label] || 0, () => c))
}

function getAdditionalLabels(d) {
    let labels = getAdditionalLabelsCounter(modelThemesToTexts[d.id]).sortedEntries()
    return labels.map(([label, count]) => ({label, count}))
}

class Counter extends Object {
    constructor() {
	super()
    }

    add(key, amount = 1) {
	if (!(key in this)) {
	    this[key] = 0
	}
	this[key] += amount
    }

    addMany(keys) {
	for (const key of keys) {
	    this.add(key)
	}
    }

    sortedEntries() {
	let entries = Object.entries(this)
	entries.sort()
	return entries
    }
}

function getBadgesCounter(theme) {
    let badges = new Counter();
    for (const text of theme.texts) {
	badges.add(getLabelForText(text));
    }
    return badges
}

function getAdditionalLabelsCounter(theme) {
    let labels = new Counter();
    for (const text of theme.texts) {
	labels.addMany(getAdditionalLabelsForText(text));
    }
    return labels
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
    console.log("renderLinks start", timing());

	// Remove the highlighting just in case
    resetLinkHighlight();
    console.log("renderLinks 1", timing());
	
//    resetLinks();
    console.log("renderLinks 2", timing());
			
    renderTermToTopicLinks();
    console.log("renderLinks 3", timing());
    
    renderTopicToTextLinks();
    console.log("renderLinks 4", timing());
    
    renderTextsToThemeLinks();
    console.log("renderLinks 5", timing());
    
    // Fix to place the links behind the containers so that the user can scroll with mouse-drag
    d3.select("#bgSvgContainer").each(function(){
                               let parent = $(this).get(0).parentNode;
                                 parent.removeChild($(this).get(0));
                                parent.insertBefore($(this).get(0), parent.firstChild);})
    console.log("renderLinks return", timing()); 
}

class Cache extends Object {
    constructor() {
	super()
    }

    get(key, valueFunction) {
	if (key in this) {
	    return this[key]
	} else {
            let value = valueFunction(key)
	    this[key] = value
	    return value
	}

    }
}

// Renders terms-to-topics links
function renderTermToTopicLinks() {
//    console.log("renderTermToTopicLinks 1",  timing());
    // If any of the lists is empty, return
    if ($("#termsList").children().length == 0
	|| $("#termsList > li.term-element:not(.not-displayed)").length == 0
	|| $("#topicsList").children().length == 0
	|| $("#topicsList > li.topic-element:not(.not-displayed)").length == 0)
	return;
  
    // Prepare the scales to map the score of the link
//    console.log("renderTermToTopicLinks 2",  timing());
    let maxScore = getMaxTermScore();
//    console.log("renderTermToTopicLinks 3",  timing());
    let opacityScale = getOpacityScale(maxScore);
//    console.log("renderTermToTopicLinks 4",  timing());
    let strokeWidthScale = getStrokeWidthScale(maxScore, TERM_TO_TOPIC_LINK_WIDTHS);
 
    // Get the position of the first term element and the first topic element
    let firstTermElement = $("#termsList > li.term-element:not(.not-displayed):first");
    let firstTopicElement = $("#topicsList > li.topic-element:not(.not-displayed):first");

    let svgId = "termLinksSvg";
//    console.log("renderTermToTopicLinks 5",  timing());
    let termLinks = prepareCanvasForLinks(firstTermElement, firstTopicElement, svgId, "termLinksHighlight");

//    console.log("renderTermToTopicLinks 6",  timing());
    let svgPos = getSvgPos(svgId);
    let leftPosCache = new Cache();
    let rightPosCache = new Cache();

    let termsList = getDisplayedElements("#termsList", (d) => d.term in modelTermsToTopics);
    let topicsList = getDisplayedElements("#topicsList");

    let linkData = []

    for (const term of termsList) {
	let relevantTopics = modelTermsToTopics[term.d.term].topics;

	for (const topic of topicsList) {
	    if (!(relevantTopics.indexOf(topic.d.id) > -1)) {
		continue;
	    }

	    let termScore = modelTermsToTopics[term.d.term].score_for_topics[modelTermsToTopics[term.d.term].topics.indexOf(topic.d.id)]
	    let text = "Topic #" + topic.d.id + "\n" + "Term: " + term.d.term + "\n" + "Score: " + termScore
	    linkData.push({
		termScore,
		term: term.d.term,
		topic: topic.d.id,
		text: text,
		rightElement: topic.element,
		leftElement: term.element,
	    })
	}
    }

    for (const e of linkData) {
	e.rightPort = rightPosCache.get(e.topic, () => linkRightPort(e.rightElement, svgPos))
	e.leftPort = leftPosCache.get(e.term, () => linkLeftPort(e.leftElement, svgPos))
    }

    drawLinks(termLinks, linkData,
	      opacityScale, strokeWidthScale,
	      "terms-to-topics");
}

function getDisplayedElements(listId, filterFunction) {
    let topicsList = [];
    d3.select(listId).selectAll("li:not(.not-displayed)")
	.each(function (d, i) {
            let topicElement = $(this);

            if (filterFunction && !(filterFunction(d)))
		return;
	    topicsList.push({
		element: topicElement,
		d: d
	    });
	});
    return topicsList;
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
    
    let svgPos = getSvgPos(svgId);
    let leftPosCache = new Cache();
    let rightPosCache = new Cache();

    let topicsList = getDisplayedElements("#topicsList", (d) => d.id in modelTopicsToDocuments);
    let textsList = getDisplayedElements("#textsList");

    let linkData = []

    for (const topic of topicsList) {
        let relevantDocumentsIndex = modelTopicsToDocuments[topic.d.id].documents_index;

	for (const text of textsList) {
	    if (!(text.d.id in relevantDocumentsIndex)) {
		continue;
	    }

	    var strokeScore = modelTopicsToDocuments[topic.d.id].topic_confidences[relevantDocumentsIndex[text.d.id]]
	    linkData.push({
		termScore:strokeScore,
		topic: topic.d.id,
		document: text.d.id,
		text: "Document #" + text.d.id + "\n" + "Topic #" +topic.d.id,
		rightElement: text.element,
		leftElement: topic.element,
	    })
	}
    }

    console.log("renderTopicToTextLinks 1", timing());
    for (const e of linkData) {
	e.rightPort = rightPosCache.get(e.document, () => linkRightPort(e.rightElement, svgPos))
	e.leftPort = leftPosCache.get(e.topic, () => linkLeftPort(e.leftElement, svgPos))
    }
    
    console.log("renderTopicToTextLinks 2", timing());

    drawLinks(links, linkData,
	      opacityScale, strokeWidthScale,
	      "topics-to-texts");
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
    
    let svgPos = getSvgPos(svgId);
    let leftPosCache = new Cache();
    let rightPosCache = new Cache();

    let themesList = getDisplayedElements("#themesList", (d) => d.id in modelThemesToTexts);
    let textsList = getDisplayedElements("#textsList");

    let linkData = []

    for (const theme of themesList) {
	let relevantTexts = modelThemesToTexts[theme.d.id].texts;

        let relevantTextsInts = []

        for (let i = 0; i < relevantTexts.length; i++){
            relevantTextsInts[i] = parseInt(relevantTexts[i])
        }

	for (const text of textsList) {
	    if (!(relevantTextsInts.indexOf(parseInt(text.d.id)) > -1)) {
		continue;
	    }

	    linkData.push({
		termScore: 1,
		text: text.d.id,
		theme: theme.d.id,
		text: "Theme #" + theme.d.id + "\n" + "Text #" + text.d.id,
		rightElement: theme.element,
		leftElement: text.element,
	    })
	}
    }

    for (const e of linkData) {
	e.rightPort = rightPosCache.get(e.theme, () => linkRightPort(e.rightElement, svgPos))
	e.leftPort = leftPosCache.get(e.text, () => linkLeftPort(e.leftElement, svgPos))
    }
    
    drawLinks(links, linkData,
	      opacityScale, strokeWidthScale,
	      "texts-to-themes");
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

// TODO: Now "prepareCanvasForLinks" is invoked several times
// it takes a lot of time. So perhaps it could be cashed in the DOM, and only
// be invoked when the window is resized.
function prepareCanvasForLinks(firstLeftElement, firstRightElement, svgId, linksHighlightId){
    let currentSvg = document.getElementById(svgId);
    if (currentSvg) {
	let svg = d3.select(currentSvg);
	let canvasvis = svg.select(".canvas-vis");

	let termlinks = canvasvis.select("#termLinks");
	termlinks.selectAll("*").remove();

	let linksHighlight = d3.select(document.getElementById(linksHighlightId));
	linksHighlight.selectAll("*").remove();

	return termlinks;
    }
    console.log("prepareCanvasForLinks 1",  timing());
    // Get the offset of the SVG element with regard to its parent container
    let elOffset = firstLeftElement.offset().left;
//    console.log("prepareCanvasForLinks 1aa",  timing());
    let parenscroll = firstLeftElement.parent().scrollLeft();
//    console.log("prepareCanvasForLinks 1ab",  timing());
    let containerOffset = $("#bgSvgContainer").offset().left;
//    console.log("prepareCanvasForLinks 1ac",  timing());
    let elOuter = firstLeftElement.outerWidth()
//    console.log("prepareCanvasForLinks 1ad",  timing());
	let svgLeft = Math.ceil(elOffset
				+ parenscroll
		 		- containerOffset
				+ elOuter);
//    console.log("prepareCanvasForLinks 1a",  timing());
	let svgTop = Math.ceil(firstLeftElement.offset().top
				+ firstLeftElement.parent().scrollTop()
				- $("#bgSvgContainer").offset().top);
//    console.log("prepareCanvasForLinks 1b",  timing());
	let svgWidth = Math.ceil(firstRightElement.offset().left
				- (firstLeftElement.offset().left + firstLeftElement.outerWidth())
		 		- 1);
    let svgHeight = Math.ceil($("#mainPanelUpper").height() - svgTop);
//    console.log("prepareCanvasForLinks 1c",  timing());
//    console.log("prepareCanvasForLinks 2",  timing());
	let svg = d3.select("#bgSvgContainer").append("svg:svg")
				.classed("svg-vis", true)
				.attr("id", svgId)
				.style("top", svgTop + "px")
				.style("left", svgLeft + "px")
				.attr("height", svgHeight + "px")
				.attr("width", svgWidth + "px")
				.attr("clip", [0, svgWidth, svgHeight, 0].join(" "));
//    console.log("prepareCanvasForLinks 3",  timing());
	// Prepare the clipping path for inner canvas
	svg.append("clipPath")
		.attr("id", "canvasClip")
	.append("rect")
	    .attr("x", 0)
	    .attr("y", 0)
	    .attr("width", svgWidth)
	    .attr("height", svgHeight);
//	console.log("prepareCanvasForLinks 4",  timing());
	let canvas = svg.append("g")
		.classed("canvas-vis", true)
		.attr("clip-path", "url(#canvasClip)");
    
//    console.log("prepareCanvasForLinks 5",  timing());
    let links = canvas.append("g")
    .attr("id", "termLinks");
    
    // Add an overlay for highlighting
    canvas.append("g")
    .attr("id", linksHighlightId);
    console.log("prepareCanvasForLinks 6",  timing());
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

function linkLeftPort(leftElement, svgPos) {
    let scrollbarWidth = 8;
    // Get the port position (this is only needed  to be calculated once, so if things get slow, do earlier)
    let leftPortX = leftElement.offset().left - svgPos.x + leftElement.outerWidth() + scrollbarWidth;
    let leftPortY = leftElement.offset().top - svgPos.y + Math.floor(leftElement.outerHeight()/2);
    return {x: leftPortX, y: leftPortY}
}

function linkRightPort(rightElement, svgPos) {
    // Get the port position
    let rightPortX = rightElement.offset().left - svgPos.x;
    let rightPortY = rightElement.offset().top - svgPos.y + Math.floor(rightElement.outerHeight()/2);
    return {x: rightPortX, y: rightPortY}
}

function getSvgPos(svgId) {
    let offsetLeft = $("#" + svgId).offset().left;
    let offsetTop = $("#" + svgId).offset().top;
    let svgPos = {x: offsetLeft, y: offsetTop}
    return svgPos;
}

// Draw the actual lines
function drawLinks(links, linkData, opacityScale, strokeWidthScale, className) {
    links
	.selectAll("line")
	.data(linkData)
	.enter()
	.append("line")
        .classed(className, true)
        .attr("x1", d => d.leftPort.x)
        .attr("y1", d => d.leftPort.y)
        .attr("x2", d => d.rightPort.x)
        .attr("y2", d => d.rightPort.y)
        .style("stroke-opacity", d => opacityScale(d.termScore))
        .style("stroke", d => strokeWidthScale(d.termScore))
        .style("stroke", "black")
        .append("svg:title")
        .text(d => d.text);
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
    setTimeout(renderLinks, 0);
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
    setTimeout(renderLinks, 0);
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
    setTimeout(renderLinks, 0);
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
    setTimeout(renderLinks, 0);
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
    console.log("sortTermsList");
	// Use the external sorting function for the terms list
	let sortFunction = SORT_TERMS[sortKey];
	
	let termsContainer = $("#termsList");
	let termElements = termsContainer.children("li.term-element").detach();
	let sortedElements = sortFunction(termElements);
	// Reset the scrolling for the container before reattaching the elements
	//termsContainer.scrollTop(0);
	termsContainer.append(sortedElements);
    console.log("sortTermsList return");
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
        setTimeout(() => highlightTermElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    else{
        $(this).removeClass(DIRECTCHOOSEN);
        setTimeout(() => highlightTermElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    
    // For the other panels, which were not recently clicked, they should show the beginning of the panel, so scroll up
    scrollTopForAllExceptRecentlyClicked("#termsList");

    
    // Sort other lists and render the links
    

    setTimeout(resetPanelHeadings, 0);
    setTimeout(setPanelHeadings, 0);
    setTimeout(resetHighlightAfterStateChange, 0);
}

function onTopicElementClick(event){
    let eventClass = $(event.target).attr("class");
    if (eventClass.includes("title-label")){
        // Discard clicks on the subcomponents within a topic element
        return;
    }
	
    let topic = d3.select($(this).get(0)).datum();
    toggleChosenElement(topic.id, modelToggleTopicElement);

    if (currentTopicIds.indexOf(topic.id) > -1){ // if chosen
        $(this).addClass(DIRECTCHOOSEN);
        setTimeout(() => highlightTopicElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    else{
        $(this).removeClass(DIRECTCHOOSEN);
        setTimeout(() => highlightTopicElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    
    // For the other panels, which were not recently clicked, they should show the beginning of the panel, so scroll up
    scrollTopForAllExceptRecentlyClicked("#topicsList");
    
    setTimeout(resetPanelHeadings, 0);
    setTimeout(setPanelHeadings, 0);
    
    setTimeout(resetHighlightAfterStateChange, 0);
}

function onTextElementClick(event){
    let eventClass = $(event.target).attr("class");
    if (eventClass.includes("choose-label-trigger") || eventClass.includes("theme-text-remove-button") ||
	eventClass.includes("text-theme-remove-glyph") || eventClass.includes("full-text") || eventClass.includes("snippet-text")){
        // Discard clicks on the subcomponents within a text element
        return;
    }

    event.preventDefault();
    
    let text = d3.select($(this).get(0)).datum();
    toggleChosenElement(text.id, modelToggleTextElement);
    
    
    // Sort other lists and render the links
    
    if (currentTextIds.indexOf(text.id) > -1){ // if chosen
        $(this).addClass(DIRECTCHOOSEN);
        setTimeout(() => highlightTextElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    else{
        $(this).removeClass(DIRECTCHOOSEN);
        setTimeout(() => highlightTextElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    
    // For the other panels, which were not recently clicked, they should show the beginning of the panel, so scroll up
    scrollTopForAllExceptRecentlyClicked("#textsList");
    
    modelSetMostRecentlyClickedForThemeRanking(text.id);
    //This sorting the rendering is not done here, but in a call-back from modelGetThemeRankingForText
    //sortThemesList(themeSortMode);
    //renderLinks();
    setTimeout(resetPanelHeadings, 0);
    setTimeout(setPanelHeadings, 0);
    
    setTimeout(resetHighlightAfterStateChange, 0);
    
   
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
        setTimeout(() => highlightThemeElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    else{
        $(this).removeClass(DIRECTCHOOSEN);
        setTimeout(() => highlightThemeElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT), 0);
    }
    
    // For the other panels, which were not recently clicked, they should show the beginning of the panel, so scroll up
    scrollTopForAllExceptRecentlyClicked("#themesList");
    setTimeout(resetPanelHeadings, 0);
    setTimeout(setPanelHeadings, 0);
    
    setTimeout(resetHighlightAfterStateChange, 0);
}



// Help function used by all all element click functions to toggle between chosen or not
function toggleChosenElement(id, modelToggleFunction){
    modelToggleFunction(id);
    fillSplittedCurrentTermList();
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
    addTextThemeLinkAndUpdateInterface(textId, theme.id)
}

// Invoked from the drag and drop text-theme association, as well as when it is done with keys
function addTextThemeLinkAndUpdateInterface(textId, themeId){
    modelAddTextThemeLink(themeId, textId);

    // Repopulate the theme element for the updated text-theme links
    let themesList = d3.select("#themesList").selectAll("li")
        .filter(function(f, j){
            return themeId == f.id;
        })
    populateThemeElements(themesList);
    
    // Adds information of associated themes to the text elements
    let textElementSelection = d3.select("#textsList").selectAll("li")
    .filter(function(f, j){
    return isAssociatedThemeText(themeId, f.id);
    });
    populateTextElement(textElementSelection);
    
    setTimeout(addChoiceBasedHighlight, 0);
    setTimeout(renderLinks, 0);
}


function onKeyDown(event) {
    const currentTime = Date.now();

    // only select a theme to attach to if a text is chosen
    if (currentTextIds.length == 0){
        return;
    }
    
    if (currentTextIds.length > 1){
        alert("Several texts are selected, you can only attach one text at a time to a theme");
        return;
    }          

    const charList = '0123456789';
    const key = event.key.toLowerCase();

    if (currentTime - lastKeyTime > 1500) {
        buffer = [];
    }
    
    if (event.key === "Enter" && buffer.length > 0){
	var keyselectedtheme = parseInt(buffer.join(''))
	addTextThemeLinkAndUpdateInterface(currentTextIds[0], keyselectedtheme)
	buffer = [];
	return;
    }
    
    if (charList.indexOf(key) == -1) return;



    buffer.push(key);
    lastKeyTime = currentTime;
    
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
    let textElementSelection = d3.select("#textsList").selectAll("li")
    .filter(function(f, j){
            return text.id == f.id;
    });
    populateTextElement(textElementSelection);
    
    // Repopulate the theme element for the updated text-theme links
    let themesList = d3.select("#themesList").selectAll("li")
	.filter(function(f, j){
            return themeId == f.id;
        })
    populateThemeElements(themesList);
    
    // Redraw the links
    setTimeout(renderLinks, 0);  
}

// Creates a new theme
function onThemeAdd() {
	createNewTheme();	
}

// Creates a new theme with an optionally provided list of text IDs
async function createNewTheme(textIds) {
    disableThemeButtons(); // To prevent the user from creating several themes at the same time
    await modelCreateNewTheme(textIds);
    controllerDoPopulateThemes();
    doDefaultSort();
}

function controllerSelectChosenAnalysis(name_of_created_analysis){
    
    $("#analysisVersion").val(name_of_created_analysis);
    $("#analysisVersion").trigger("change");
}

function controllerDoPopulateThemes(){
    $("#themesList").empty();
	// Update the list elements with D3
    let themesList = d3.select("#themesList").selectAll("li")
	// Note the function below used to ensure the correct mapping of existing elements
	// despite the arbitrary DOM ordering after sorting
	.data(modelThemes, function(d) { return d.id; })
	.enter()
	.append("li")
    populateThemeElements(themesList);
        
    enableThemeButtons();
}
                                                                        
function controllerRepopulateTheme(){
    let themesList = d3.select("#themesList").selectAll("li");
    populateThemeElements(themesList);
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
    setTimeout(renderLinks, 0);
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

function timing() {
    let now = Date.now();
    let diff = now - timing.last;
    timing.last = now;
    return diff;
}

function doResetHighlightAfterStateChange(){
    console.log("doResetHighlightAfterStateChange", timing());
    // If a term is not selected
    if (currentTermIds.length == 0){
        sortTermsList(termSortMode);
    }
    
    // If a topic is not selected
    if (currentTopicIds.length == 0 && currentTermIds.length == 0){
        sortTopicsList(topicSortMode);
	d3.selectAll(".term-to-mark").classed("specifictermchosen", true);
	d3.selectAll(".term-to-mark").classed("termintextnotchosen", true);
    }
    
    else{
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
	d3.selectAll(".term-to-mark").classed("specifictermchosen", false);
    }
    
    // If a text is not selected
    if (currentTextIds.length == 0){
        sortTextsList(textSortMode);
    }

    (async () => {
	// If a theme is not selected
	if (currentThemeIds.length == 0){
            await modelSortThemesWithMachineLearningIfTextChosen();
	    sortThemesList(themeSortMode);
	}
	
	setTimeout(addChoiceBasedHighlight, 0);
	console.log("doResetHighlightAfterStateChange return", timing());
	
	console.log("doResetHighlightAfterStateChange before renderLinks", timing());
	setTimeout(renderLinks, 0);
    })();
}


function resetPanelHeadings(){
    d3.select("#termsContainer").select(".containerheader").classed("panel-heading-marked", false);
    d3.select("#topicsContainer").select(".containerheader").classed("panel-heading-marked", false);
    d3.select("#textContainer").select(".containerheader").classed("panel-heading-marked", false);
    d3.select("#themesContainer").select(".containerheader").classed("panel-heading-marked", false);
    
    d3.select("#termsContainer").classed("panel-marked", false);
    d3.select("#topicsContainer").classed("panel-marked", false);
    d3.select("#textContainer").classed("panel-marked", false);
    d3.select("#themesContainer").classed("panel-marked", false);
}

function setPanelHeadings(){
    if (currentTermIds.length > 0){
        d3.select("#termsContainer").select(".containerheader").classed("panel-heading-marked", true);
        d3.select("#termsContainer").classed("panel-marked", true);
    }
    if (currentTopicIds.length > 0){
        d3.select("#topicsContainer").select(".containerheader").classed("panel-heading-marked", true);
        d3.select("#topicsContainer").classed("panel-marked", true);
    }
    if (currentTextIds.length > 0){
        d3.select("#textContainer").select(".containerheader").classed("panel-heading-marked", true);
        d3.select("#textContainer").classed("panel-marked", true);
    }
    if (currentThemeIds.length > 0){
        d3.select("#themesContainer").select(".containerheader").classed("panel-heading-marked", true);
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
    console.log("addChoiceBasedHighlight");    
    
    // If there are selected items, first set all items to grey
      
    d3.selectAll("." + DIRECTCHOOSEN)
    .classed(DIRECTCHOOSEN, false);
    
    d3.selectAll("." + CHOOSEN)
    .classed(CHOOSEN, false);
    
    d3.selectAll("." + NOTCHOSEN)
	.classed(NOTCHOSEN, false);

    
    /*
    // Reset to show snippet texts only
    d3.selectAll('.snippet-text').classed("not-displayed-text", false);
    d3.selectAll('.full-text').classed("not-displayed-text", true);
    d3.selectAll('.snippet-text').classed("displayed-text", true);
    d3.selectAll('.full-text').classed("displayed-text", false);
    showFullText = false;
    $("#showFullText").removeClass("button-active");
    */
                                                        
    d3.selectAll('.text-label').classed("text-border", false);
    
    // Reset highlight of terms that stem from topics that are not chosen
    
    // Then go through all items to see which are selected
    // and set them to not grey

    console.log("addChoiceBasedHighlight #termsList");
    d3.select("#termsList").selectAll("li")
    .each(function(d, i){
          let element = $(this);
          if (currentTermIds.indexOf(d.term) > -1){
            highlightTermElement(element, DIRECTCHOOSEN, CHOOSEN);
          }
          });
 
    
    console.log("addChoiceBasedHighlight #topicsList");
    d3.select("#topicsList").selectAll("li")
    .each(function(d, i){
          let element = $(this);
          if (currentTopicIds.indexOf(d.id) > -1){
            highlightTopicElement(element, DIRECTCHOOSEN, CHOOSEN);
          }
          });
    
    
    console.log("addChoiceBasedHighlight #textsList");
    d3.select("#textsList").selectAll("li")
    .each(function(d, i){
          let element = $(this);
          if (currentTextIds.indexOf(d.id) > -1){
          highlightTextElement(element, DIRECTCHOOSEN, CHOOSEN);
          }
          });
    
    console.log("addChoiceBasedHighlight #themesList");
    d3.select("#themesList").selectAll("li")
    .each(function(d, i){
          let element = $(this);
          if (currentThemeIds.indexOf(d.id) > -1){
          highlightThemeElement(element, DIRECTCHOOSEN, CHOOSEN);
          }
          });

    console.log("addChoiceBasedHighlight reset");
    resetAllArgumentMarkings();
    console.log("addChoiceBasedHighlight return");
}


// Handles hovering for a document element
function onTextElementMouseEnter() {
    resetHighlight();
    highlightTextElement($(this), DIRECTHIGHLIGHT, HIGHLIGHT);
    //($(this), DIRECTHIGHLIGHT, HIGHLIGHT);
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
        showFullTextChosen(textElement);
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

function showFullTextChosen(textElement){
    //d3.select(textElement.get(0)).selectAll('.text-label').classed("text-border", true);
    d3.select(textElement.get(0)).selectAll('.snippet-text').classed("not-displayed-text", true);
    d3.select(textElement.get(0)).selectAll('.full-text').classed("not-displayed-text", false);

    d3.select(textElement.get(0)).selectAll('.snippet-text').classed("displayed-text", false);
    d3.select(textElement.get(0)).selectAll('.full-text').classed("displayed-text", true);

    
    let textId = d3.select(textElement.get(0)).datum().id;
    
    // if current text is selected
    //if (currentTextIds.indexOf(textId) > -1){
   //     colorAllTagsWithTheSameColor(textElement);
   // }
}


function secondaryHighlightTermsInText(textElement){
    let textId = d3.select(textElement.get(0)).datum().id;

    
    // If topics are chosen, hightlight terms that belong to thees topics, and in accordance to the strength of these terms to these topics
    /*
    d3.select(textElement.get(0)).selectAll(".term-to-mark").classed("specifictermchosen", false);
    
    if (modelTopics != []){
        for (let i = 0; i < modelTopics.length; i++) {
            let topic = modelTopics[i]["id"];
            // If topic is selected
            if (currentTopicIds.indexOf(topic) > -1){
                d3.select(textElement.get(0)).selectAll('.topic_' + topic).classed("termintextnotchosen", false);
            }
	    
            else{
                d3.select(textElement.get(0)).selectAll('.topic_' + topic).classed("termintextnotchosen", true);
            }
        }
    }*/

    // If terms are chosen, highlight these terms
    if (currentTermIds.length > 0){
        // Default is that nothing is marked
        //d3.select(textElement.get(0)).selectAll(".term-to-mark").classed("specifictermchosen", false);
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

    setTimeout(renderLinks, 0);

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
	setTimeout(renderLinks, 0);
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
	setTimeout(renderLinks, 0);
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
	setTimeout(renderLinks, 0);
}


////////
// Hide ans show search buttons
////////

// All fields
function hideSearchFields(){
    let field_names = ["#termSearch", "#termSearchClear", "#topicSearch", "#topicSearchClear", "#textSearch", "#textSearchClear", "#themeSearch", "#themeSearchClear"];
    for (let i = 0; i < field_names.length; i++){
        d3.select(field_names[i]).style("display", "none");
    }
}

// Help functions
function showSearchField(fieldName, clearName, showFieldClass){
    d3.select(fieldName).style("display", "block");
    d3.select(fieldName).classed(showFieldClass, true)
    d3.select(clearName).style("display", "block");
    d3.select(fieldName).each(function(){
                              $(this).focus()
                              })
}

function hideSearchField(fieldName, clearName, showFieldClass){
    d3.select(fieldName).style("display", "none");
    d3.select(fieldName).classed(showFieldClass, false)
    d3.select(clearName).style("display", "none");
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
    controllerDoPopulateThemes();

    // Resize the containers
    resizeContainers();
    
    // Redraw the links
    setTimeout(renderLinks, 0);
}

function onDoThemeSorting(){
    doThemesSorting = !doThemesSorting;
    if (doThemesSorting){
	$("#doThemeSorting").addClass("button-active");
	doResetHighlightAfterStateChange();
    }
    else{
        modelResetRecentlyClickedForMachineLearningSorting();
        $("#doThemeSorting").removeClass("button-active");
    }
}

function onShowFullText(){
    if (showFullText){
        showFullText = false; // show snippet text
	d3.selectAll('.snippet-text').classed("not-displayed-text", false);
	d3.selectAll('.full-text').classed("not-displayed-text", true);
	
	d3.selectAll('.snippet-text').classed("displayed-text", true);
	d3.selectAll('.full-text').classed("displayed-text", false);

	$("#showFullText").removeClass("button-active");
    }
    else{
        showFullText = true;

	d3.selectAll('.snippet-text').classed("not-displayed-text", true);
	d3.selectAll('.full-text').classed("not-displayed-text", false);
	
	d3.selectAll('.snippet-text').classed("displayed-text", false);
	d3.selectAll('.full-text').classed("displayed-text", true);

	
	$("#showFullText").addClass("button-active");

    }

    //modelResetClickedChoices();
    //resetPanelHeadings();
    //doResetHighlightAfterStateChange();
    //controllerDoPopulateInterface();
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

function onResizeTerms(){
    if (termsSmall){
        termsSmall = false;
        $("#resizeTerms").removeClass("button-active");
        $("#resizeTerms").removeClass("header-button-small");
        $("#resizeTerms").addClass("header-button");
	$("#mainPanel").removeClass("terms-small");

	$("#lockTermsSorting").removeClass("header-button-hidden");
	$("#termSearchButton").removeClass("header-button-hidden");
	$("#termSortButton").removeClass("header-button-hidden");

	d3.select("#termsTitle").text("Terms");
	hideSearchFields();
	doResetHighlightAfterStateChange();
    }
    else{
        termsSmall = true;
	$("#mainPanel").addClass("terms-small");
        $("#resizeTerms").addClass("button-active");

	$("#lockTermsSorting").addClass("header-button-hidden");
	$("#termSearchButton").addClass("header-button-hidden");
	$("#termSortButton").addClass("header-button-hidden");

	d3.select("#termsTitle").text("");

	hideSearchFields();
	doResetHighlightAfterStateChange();

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

$("#sentiment").on("click", onShowSentiment);
$("#claim").on("click", onShowClaim);
$("#supporting").on("click", onShowSupporting);
$("#opposing").on("click", onShowOpposing);

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


$(document).on("click", function (e) {
    $(".popupmenu").parent().removeClass('popupmenu-open');
});


function popupmenuclick(e) {
    let button = $(this);

    if (button.is('.disabled')) {
	return;
    }

    if (button.parent().hasClass('popupmenu-open')) {
	$(".popupmenu").parent().removeClass('popupmenu-open');
    } else {
	$(".popupmenu").parent().removeClass('popupmenu-open');
	button.parent().addClass('popupmenu-open');
    }

    e.preventDefault();
    e.stopPropagation();
}

$(".popupmenu").on("click", popupmenuclick);
