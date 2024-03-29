"use strict";


// The URL to communicate with the restful api. Looking at the local server at the
// moment.
//var BASEURL = "http://127.0.0.1:5000/topics2themes/api/v1.0/"

var BASEURL = "/topics2themes/api/v1.0/"

// The original JSON data set that contains the topic model
var jsonData;

///The data, model and analysis choices
// The database id of the topic model that is currently being worked on
var modelCurrentModelId;

// The currently selected dataset name
var modelCurrentDataset;

// The datasets that are available in the data set directory
var modelDataSetChoices;

// The models that are available for the currentDataset
var modelModelsForCurrentDataset;

// The currently selected analysis ID
var modelCurrentAnalysisVersionId = null;

// The analyses that are available for the currently selected model
var modelAnalysesForCurrentModel;

// Name of currently selected analysis
var modelCurrentAnalysisName;


// Topic term entries
var modelTerms;

// Topics
var modelTopics = [];


// Theme entries
var modelThemes;

// Text document entries
var modelDocuments;

var modelLabelCategories;
var modelCategoryToColor;

// Mapping of terms to topics
var modelTermsToTopics;
// Mapping of terms to documents
var modelTermsToDocuments;
// Mapping of topics to documents
var modelTopicsToDocuments;
// Mapping of texts to themes
var modelThemesToTexts;
// Mapping of themes to texts
var modelTextsToThemes;


// The topics that have been given user names
var modelTopicNames;
//
var modelUserTextLabels;

// The terms that are selected
var currentTermIds = new Set();
// The topics that are selected
var currentTopicIds = new Set();
// The documents that are selected
var currentTextIds = new Set();
// The themes that are selected
var currentThemeIds = new Set();

// Used for sorting the themes that are not currently selected
var modelMostRecentlyClickedText;
var modelThemeRankingForMostRecentlyClickedText = [];

var modelShowArgumentation = undefined;

var modelShowSentiment = undefined;

var modelDisableModelCreation = undefined;
var modelAnalysisExportEnabled = undefined;

////////////////
// Comparators for sorting
///////////////

//
function compareValuesThemesRankingAscMachineLearning(a, b){
    let index_a = modelThemeRankingForMostRecentlyClickedText.indexOf(a["id"].toString());
    let index_b = modelThemeRankingForMostRecentlyClickedText.indexOf(b["id"].toString());

    return index_a - index_b;
}


// Utility comparator
function compareNumbersAsc(a, b) {
  return a - b;
}

// Utility comparator
function compareNumbersDesc(a, b) {
  return b - a;
}

// Utility comparator for temporary value arrays
function compareValuesAsc(a, b) {
    if (a.value == b.value && 'secondaryValue' in a && 'secondaryValue' in b){
        return a.secondaryValue - b.secondaryValue;
    }
  return a.value - b.value;
}

// Utility comparator for temporary value arrays
function compareValuesDesc(a, b) {
    if (a.value == b.value && 'secondaryValue' in a && 'secondaryValue' in b){
        return b.secondaryValue - a.secondaryValue;
    }
  return b.value - a.value;
}

// Utility comparator for id value arrays
function compareIdAsc(a, b) {
    return a.id - b.id;
}
// Utility comparator for id value arrays
function compareIdDesc(a, b) {
    return b.id - a.id;
}

// Utility comparator for number of texts value arrays
function compareNumberOfTextsAsc(a, b) {
    return a.numberOfTexts - b.numberOfTexts;
}

// Utility comparator for number of texts value arrays
function compareNumberOfTextsDesc(a, b) {
    return b.numberOfTexts - a.numberOfTexts;
}

// Utility comparator for temporary value arrays
function compareStringValuesAsc(a, b) {
  return a.value.localeCompare(b.value);
}

// Utility comparator for temporary value arrays
function compareStringValuesDesc(a, b) {
  return b.value.localeCompare(a.value);
}

// Topic terms comparator
function compareTopicTermsDesc(a, b){
	return b.score - a.score;
}


// Resets the stored data values
/*
function resetData() {
	// Reset the internal data
    resetModelData()
    modelCurrentDataset = null;
    modelDataSetChoices = [];
    modelModelsForCurrentDataset = [];
}
 */

// When a new dataset is selected, previously shown model selection data should reset (and therefore no analysis data)
function resetModelChoiceData(){
    modelCurrentModelId = null;
    modelModelsForCurrentDataset = [];
    resetAnalysisChoiceData()
}

// When no model is selected, no data related to analysis can be presented
function resetAnalysisChoiceData(){
    modelAnalysesForCurrentModel = [];
    modelCurrentAnalysisVersionId = null;
}



function resetModelData(){
    jsonData = [];
    modelTerms = [];
    modelTermsToTopics = new Map();
    modelTermsToDocuments = new Map();
    modelTopicsToDocuments = new Map();
    modelTopics = [];
    modelDocuments = new Map();
    modelLabelCategories = [];
    modelCategoryToColor = {};
    resetSelectedDataExcept();
    resetUserAnalysisData();
    resetAnalysisChoiceData();

}

function resetUserAnalysisData(){
    modelThemes = [];
    modelThemesToTexts = new Map();
    modelTextsToThemes = new Map();
    modelTopicNames = new Map();
    modelUserTextLabels = {};
    
    modelResetRecentlyClickedForMachineLearningSorting();
    modelResetClickedChoices();
}

function modelResetClickedChoices(){
    currentTermIds.clear();
    currentTopicIds.clear();
    currentTextIds.clear();
    currentThemeIds.clear();
}

// Resets all list of selected items, except the argument (if such an argument is submitted)
function resetSelectedDataExcept(notToReset){
    if (notToReset !== currentTermIds) {
        currentTermIds.clear();
    }
    
    if (notToReset !== currentTopicIds) {
        currentTopicIds.clear();
    }
    
    if (notToReset !== currentTextIds) {
        currentTextIds.clear();
    }
    
    if (notToReset !== currentThemeIds) {
        currentThemeIds.clear();
    }
}

async function modelCreateNewTheme(){
    if (modelCurrentAnalysisVersionId == null){
	// Don't create new themes if no analysis has been selected
	return;
    }
    let createThemeUrl = "create_new_theme";
    let data = {"analysis_id" : modelCurrentAnalysisVersionId};
    let themeId = await save_data_async(createThemeUrl, data);

    addNewTheme(themeId, "");
}

//
function addNewTheme(themeId, newLabel){
    var d = new Date();
    var currentTime = d.getTime();
    
    modelThemes.push({
                     id: themeId,
                     label: newLabel,
                     creation_time: currentTime
                     });
    
    modelThemesToTexts.set(themeId, {
        "texts" : new Set()
    })
}

/////////
// General functionality used for communicating with server
///////

async function get_data_async(url, dataToSend) {
    dataToSend["authentication_key"] = authenticationKey
    let result = await $.ajax({
	url:BASEURL + url,
	dataType: "json",
	data: dataToSend,
	type: "GET"
    });
    return result["result"];
}

function get_data(url, success_function, dataToSend) {
    (async () => {
	try {
	    let result = await get_data_async(url, dataToSend);
	    success_function(result);
	} catch (jqXHR) {
	    alert("Something went wrong with " + url)
	}
    })();
}


async function save_data_async(url, dataToSend) {
    dataToSend["authentication_key"] = authenticationKey
    let result = await $.ajax({
	url:BASEURL + url,
	dataType: "json",
	data: dataToSend,
	type: "POST"
    });
    return result["result"];
}

function save_data(url, success_function, dataToSend) {
    (async () => {
	try {
	    let result = await save_data_async(url, dataToSend);
	    success_function(result);
	} catch (jqXHR) {
	    alert("Something went wrong with " + url)
	}
    })();    
}
	
// Initializes the data entries
async function modelInitializeData(modelId) {
    modelCurrentModelId = modelId;
    let res = await get_data_async("get_model_for_model_id", {"model_id" : modelId});
    resetModelData()
    jsonData = res["topic_model_output"];
    let documents = jsonData.documents;
	let topics = jsonData.topics;
    
    let labelCategories = jsonData["meta_data"]["configuration"]["DATA_LABEL_LIST"]
    modelLabelCategories = [];
    modelCategoryToColor = {};
    for (const labelCategory of labelCategories)
    {
        var color = "silver";
        if ("label_color" in labelCategory){
            color = labelCategory["label_color"]
        }
        modelLabelCategories.push({"label" : labelCategory["data_label"], "color" : color})
	modelCategoryToColor[labelCategory["data_label"]] = color;
    }

    if (jsonData["meta_data"]["SHOW_ARGUMENTATION"] == "True"){
	modelShowArgumentation = 1;
    }
    else{
	modelShowArgumentation = undefined;
    }
    if (jsonData["meta_data"]["SHOW_SENTIMENT"] == "True"){
	modelShowSentiment = 1;
    }
    else{
	modelShowSentiment = undefined;
    }
    
   

    // Terms have to be constructed from topics
    // At the same time, the reverse mapping from terms to topics should be established
    for (const topic of topics) {
        modelTopics.push({"id" : topic.id, "defaultlabel" : topic.label})

        if (topic.topic_terms == undefined){
            alert("Terms missing for topic number  " +  topic.id);
                        continue;
        }

        for (const topic_term of topic.topic_terms) {
            modelTermsToTopics.setdefault(topic_term.term, {
                "term": topic_term.term,
                "score_for_topics": new Map()
            }).score_for_topics.set(topic.id, topic_term.score)
            maxTermScoreCache = undefined;
        }
    }

    // Extract the array of values from the dictionary
    modelTerms = Array.from(modelTermsToTopics.values());

    // Establish the reverse mappings from topics to documents and terms to documents
    modelTopicsToDocuments.clear()
    modelTermsToDocuments.clear()

        for (var doc of documents) {
	
		// NOTE: "document" is a pretty important DOM object,
		// so better use other local variable names

            // TODO: This code (and the check if snippet exists below) is only here for historic reasons. Remove in later version
            let dot_splitted = doc.marked_text_tok.split(".").slice(0,2);
            let snippet = dot_splitted.join(".") + "... [TEMPORARY SUM.]"
  
            if("snippet" in doc){
		snippet = doc.snippet
            }
        /*
        let snippetVersion = doc.marked_text_tok
        if doc.marked_text_tok.length > 100:
            snippetVersion = doc.marked_text_tok.substring()
            */
            modelDocuments.set(doc.id, {"id" : doc.id, "text" : doc.text, "label": doc.label, "marked_text_tok": doc.marked_text_tok, "additional_labels" : doc.additional_labels, "snippet": snippet, "base_name" : doc.base_name})
		
		if (doc.document_topics == undefined)
			continue;
		
                for (const doc_topic of doc.document_topics) {
                    modelTopicsToDocuments.setdefault(doc_topic.topic_index, {
                            "topic": doc_topic.topic_index,
                            "documents": new Set(),
                            "topic_confidences" : new Map()
                    })
                    modelTopicsToDocuments.get(doc_topic.topic_index).documents.add(doc.id);
                    modelTopicsToDocuments.get(doc_topic.topic_index).topic_confidences.set(doc.id, doc_topic.topic_confidence)

                    for (const doc_term of doc_topic.terms_in_topic) {
                        modelTermsToDocuments.setdefault(doc_term.term, {
                            "term": doc_term,
                            "documents": new Set()
                        }).documents.add(doc.id)
                    }
                }
	}
    
}


function getScoreForTermTopic(term, topicId){
    return modelTermsToTopics.get(term).score_for_topics.get(topicId);
}

function getLabelForText(textId){
    let modelDocument = modelDocuments.get(textId)
    if (modelDocument === undefined) {
        return undefined
    }
    return modelGetTextLabelForId(modelDocument.id) ?? modelDocument.label
}

function getAdditionalLabelsForText(textId){
    let modelDocument = modelDocuments.get(textId)
    if (modelDocument === undefined) {
        return undefined
    }
    return modelDocument.additional_labels.sort();
}

////
// For getting the maximum score for the four categories (used for sorting)
////
let maxTermScoreCache;

function getMaxTermScore(){
    if (maxTermScoreCache === undefined) {
        let all_scores = _.flatten(modelTermsToTopics.map(([k, v]) => Array.from(v.score_for_topics.values())), 1);
        let max_score = _.max(all_scores)
        maxTermScoreCache = max_score
        return max_score
    } else {
        return maxTermScoreCache
    }
}

// Get the maximum creation data
function getMaxThemeScore(){
    let all_scores = _.map(modelThemes, (v) => v.creation_time);
    
    return _.max(all_scores)
}

function getMaxTopicScore(){
    // Let the score of a topic be the total score for the terms that belong to it
    // TODO: This code is duplicated, make a function
    let all_scores = modelTopics.map(topic =>
                                     sum(modelTermsToTopics.map(([k, v]) =>
                                                                v.score_for_topics.get(topic.id) ?? 0)))
    return _.max(_.flatten(all_scores, 1))
}

function getMaxDocumentScore(){
    return _.max(modelTopicsToDocuments.map(([k, v]) => _.max(Array.from(v.topic_confidences.values()))));
}



function modelAddTextThemeLink(themeId, textId){
    if (!modelThemesToTexts.has(themeId)) {
        console.log("themeId not in modelThemesToTexts");
        console.log(themeId);
        return;
    }

    modelThemesToTexts.get(themeId).texts.add(textId)

    modelTextsToThemes
        .setdefault(textId, {"themes" : new Set()})
        .themes.add(themeId)

    let addTextThemeLinkUrl = "add_theme_document_connection";
    let data = {"theme_number" :themeId,
        "document_id":textId, "analysis_id": modelCurrentAnalysisVersionId};

    (async () => {
	save_data_async(addTextThemeLinkUrl, data);
    })();
}

function hasThemeAssociatedTexts(themeId){
    return modelThemesToTexts.get(themeId)?.texts.size > 0
}


function removeTheme(themeId){
    if (hasThemeAssociatedTexts(themeId)){
        return false; // It is not allowed to delete themes that have associated texts.

    }
    let index = modelThemes.findIndex(function(e){ return e.id == themeId; });
    if (index < 0)
    	return false;

    modelThemes.splice(index, 1);
    modelThemesToTexts.delete(themeId);
    
    deleteDatabaseTheme(themeId)
    // Reset all selections when a theme is removed
    resetSelectedDataExcept();
    
    return true;
}

async function removeTextThemeLink(themeId, textId){
    modelThemesToTexts.get(themeId).texts.delete(textId);
    
    modelTextsToThemes.get(textId).themes.delete(themeId);

    await deleteDatabaseTextThemeLink(themeId, textId);
}


function modelSetMostRecentlyClickedForThemeRanking(textId){
    // TODO: Chosing not to sort after it already has been sorted doesn't seem to work
    if (!currentTextIds.has(textId) || modelCurrentAnalysisVersionId == null || !doThemesSorting) {
        // Then it was an unclick a previously selected text
        if (currentTextIds.size == 0){
            // If no more documents are selected, reset the machine learning based theme sorting
            modelResetRecentlyClickedForMachineLearningSorting();
        }
        if (!doThemesSorting && currentTextIds.has(textId)) {
            modelMostRecentlyClickedText = textId; // Save to use for later if doThemesSorting would be enabled
        }
        
        return;
    }
    //else:
    modelMostRecentlyClickedText = textId; // Used for sorting the themes that are not currently selected
}


async function modelSortThemesWithMachineLearningIfTextChosen(){
    if(modelMostRecentlyClickedText == undefined){
	return;
    }

    let themeRankingUrl = "get_theme_ranking_for_document";
    let data = {"document_id" : modelMostRecentlyClickedText, "analysis_id" : modelCurrentAnalysisVersionId};

    modelThemeRankingForMostRecentlyClickedText = await get_data_async(themeRankingUrl, data);
}


function sum(array) {
    return array.reduce((acc, e) => acc + e, 0);
}

// Calculates the total score for the provided array of term list elements
function calculateTermsScore(termElements) {
    return $.map(termElements, function(element, i) {
	let d = d3.select(element).datum();

	// The isRelated* flags below are used to sort the selected elements separately
	// to ensure proper sorting for all sorting modes (desc/asc)

	let currentAssociatedTermTopics = currentTopicIds.filter(currentTopicId => isAssociatedTermTopic(d.term, currentTopicId));
	let isRelatedTopicSelected = currentAssociatedTermTopics.length > 0;

	if (isRelatedTopicSelected) {
	    let scores = currentAssociatedTermTopics.map((currentTopicId) => getScoreForTermTopic(d.term, currentTopicId))

	    let accScore = sum(scores)

            return { index: i, element: element, value: accScore, isSelected: true, secondaryValue: d.term.length };
	} else {
            let isRelatedTextSelected = currentTextIds.some(text => isAssociatedTextTerm(text, d.term))
	    let isRelatedThemeSelected = currentThemeIds.some(theme => isAssociatedThemeTerm(theme, d.term))

	    let associatedTermTopics = modelTopics.filter(topic => isAssociatedTermTopic(d.term, topic.id))

	    let scores = associatedTermTopics.map((topic => getScoreForTermTopic(d.term, topic.id)))

	    let accScore = sum(scores)

            return { index: i, element: element, value: accScore, isSelected: isRelatedTextSelected || isRelatedThemeSelected, secondaryValue: d.term.length };
	}
    });
}


// Calculates the total score for the provided array of text list elements
function calculateTextScore(textElements) {
    return $.map(textElements, function(element, i){
        let d = d3.select(element).datum();

	// The isRelated* flags below are used to sort the selected elements separately
	// to ensure proper sorting for all sorting modes (desc/asc)

	let currentAssociatedTextTopics = currentTopicIds.filter(currentTopicId => isAssociatedTextTopic(d.id, currentTopicId));
	let isRelatedTopicSelected = currentAssociatedTextTopics.length > 0;

	if (isRelatedTopicSelected) {
	    let accScore = sum(currentAssociatedTextTopics.map(currentTopicId => modelTopicsToDocuments.get(currentTopicId).topic_confidences.get(d.id)))
            return { index: i, element: element, value: accScore, isSelected: isRelatedTopicSelected, secondaryValue: -1*d.text.length};
	}
	let associatedTextTopics = modelTopics.filter(topic => isAssociatedTextTopic(d.id, topic.id));

        // This is the standard score to give to the term, an
        // accumulation of each topic it
        // is associated to, if no topic is chosen
        let scores = associatedTextTopics.map(topic => modelTopicsToDocuments.get(topic.id).topic_confidences.get(d.id))

        // When no topic is chosen, use the mean strength for the topics
        let accScore = sum(scores) / scores.length;

	let isRelatedTermSelected = currentTermIds.some(term => isAssociatedTextTerm(d.id, term))

        let isRelatedThemeSelected = currentThemeIds.some(theme => isAssociatedTextTheme(d.id, theme))

        // Prepare the resulting element
        // If the association score is the same, sort according to inverse document length, as a short document with high association should have a higher expressiveness
        return { index: i, element: element, value: accScore, isSelected: isRelatedTermSelected || isRelatedThemeSelected, secondaryValue: -1*d.text.length};
    });
}

function isAssociatedSelectedForText(textId) {
    let isRelatedTopicSelected = modelTopics.some(topic => isAssociatedTextTopic(textId, topic.id) && currentTopicIds.has(topic.id));
    let isRelatedTermSelected = modelTerms.some(term => isAssociatedTextTerm(textId, term.term) && currentTermIds.has(term.term));
    let isRelatedThemeSelected = modelThemes.some(theme => isAssociatedTextTheme(textId, theme.id) && currentThemeIds.has(theme.id));

    return isRelatedTopicSelected || isRelatedTermSelected || isRelatedThemeSelected
}

function calculateTextThemesScore(textElements) {
    return $.map(textElements, function(element, i){
        let d = d3.select(element).datum();
        let number = modelTextsToThemes.get(d.id)?.themes.size ?? 0;

        // The flag below is used to sort the selected elements separately
        // to ensure proper sorting for all sorting modes (desc/asc)
        let isSelected = isAssociatedSelectedForText(d.id)

        // Prepare the resulting element
        return { index: i, element: element, value: number, isSelected: isSelected };
    });
}


function getLabelForSort(textElements) {
    return $.map(textElements, function(element, i){

        let d = d3.select(element).datum();
        let label = modelUserTextLabels[d.id] ?? d.label

        // The flag below is used to sort the selected elements separately
        // to ensure proper sorting for all sorting modes (desc/asc)
        let isSelected = isAssociatedSelectedForText(d.id)

        // Prepare the resulting element
        return { index: i, element: element, value: label, isSelected: isSelected};
    });
}


// Calculates the total score for the provided array of text list elements
// TODO: When a term or a document is chosen, no ordering of which topic is MOST related to this term or document is given (all related get same score)
// perhaps this should be added
function calculateTopicScore(topicElements) {
    return $.map(topicElements, function(element, i){
                 let d = d3.select(element).datum();

                 
                 // TODO: Enable a sorting based on total term score as well
                // Code for computing the total term score for a topic
                 // Not used at the moment
                 /*
                 var tot_score = 0;
                 let termScores = [];
                 let nrTopTermsToTakeIntoAccountForTopicScore = 5;
                 
                    $.each(modelTermsToTopics, function(k, v){
                        let topic_index = v.topics.indexOf(d.id);
                        if (topic_index > -1){
                            termScores.push(v.score_for_topics[topic_index]);
                            }
                        });
                  
                 
                 termScores = termScores.sort(function(a, b){return b-a});
                 if (termScores.length <= nrTopTermsToTakeIntoAccountForTopicScore){
                 nrTopTermsToTakeIntoAccountForTopicScore = termScores.length -1;
                 }
                 for (let j = 0; j < nrTopTermsToTakeIntoAccountForTopicScore; j++){
                 tot_score = tot_score + termScores[j];
                 }
                 
                 // Use mean score of the nrTopTermsToTakeIntoAccountForTopicScore highest ranked terms
                 // for ranking the topics (mean since, if there would be fewer than nrTopTermsToTakeIntoAccountForTopicScore
                 // terms for a topic, this would be disfavoured otherwise
                 
                 tot_score = tot_score/nrTopTermsToTakeIntoAccountForTopicScore;
                 */
                  
                 // Let the score of a topic be the mean score for the texts that
                 // belong to it
                 
        // Compute the means score among the associated text
        let associations = Array.from(modelTopicsToDocuments.values()).filter(v => v.documents.has(d.id))
        let textScores = associations.map(v => v.topic_confidences.get(d.id))
        let totTextScore = sum(textScores);
        let finalTextScore = totTextScore/textScores.length;

        
        let isRelatedTermSelected = currentTermIds.some(term => isAssociatedTermTopic(term, d.id))
                 
        let isRelatedTextSelected = currentTextIds.some(text => isAssociatedTextTopic(text, d.id))
   
        let isRelatedThemeSelected = currentThemeIds.some(theme => isAssociatedThemeTopic(theme, d.id))
                
        return { index: i, element: element, value: finalTextScore, isSelected: isRelatedTermSelected || isRelatedTextSelected || isRelatedThemeSelected};
    });
    
}


// Calculates the total score for the provided array of text list elements
function calculateThemesScore(themeElements) {
    return $.map(themeElements, function(element, i) {
        let d = d3.select(element).datum();
        // Use creation time to dedice how to sort
        let tot_score = d.creation_time;

        // The flags below are used to sort the selected elements separately
        // to ensure proper sorting for all sorting modes (desc/asc)

        let isRelatedTopicSelected = currentTopicIds.some(topic => isAssociatedThemeTopic(d.id, topic));
        let isRelatedTermSelected = currentTermIds.some(term => isAssociatedThemeTerm(d.id, term));
        let isRelatedTextSelected = currentTextIds.some(text => isAssociatedTextTheme(text, d.id));

        let numberOfAssociateTexts = modelThemesToTexts.get(d.id).texts.size;

        return { index: i, element: element, value: tot_score,
                 isSelected: isRelatedTopicSelected || isRelatedTermSelected || isRelatedTextSelected,
                 id: d.id, numberOfTexts: numberOfAssociateTexts };
    });
}

// Help function for sorting element, called by all sorting functions
function sortElements(elements, calculateScoreFunction, compareValuesFunctionSelected, compareValuesFunctionOther){

    
    // Don't do any sorting (because lock sorting has been selected
    if (compareValuesFunctionSelected == null){
	return elements;
    }


    let sortValues = calculateScoreFunction(elements);
    
    // Divide into two sublists to treat selected elements separately
    let selectedSortValues = sortValues.filter(function(e){return e.isSelected;});
    let otherSortValues = sortValues.filter(function(e){return !e.isSelected;});
    
    // Sort according to the desired criterium
    selectedSortValues.sort(compareValuesFunctionSelected);
    

    // Create the resulting list
    let sortedSelectedElements = selectedSortValues.map(function(element){
                                                        return elements[element.index];
                                                        });
   
    // Is only used when sorting themes, and when there is a recently clicked text element, and the user has not selected to lock this kind of sorting
    // (It is only when sortElements for themes is envoked that compareValuesFunctionOther != null)
    if (modelMostRecentlyClickedText != undefined && doThemesSorting && compareValuesFunctionOther != null){
        otherSortValues.sort(compareValuesFunctionOther);
    }
    else{
	//TODO: Perhaps this can be changed to speed up sorting
        otherSortValues.sort(compareValuesFunctionSelected)
    }
    let sortedOtherElements = otherSortValues.map(function(element){
                                                  return elements[element.index];
                                                  });
    let result = sortedSelectedElements.concat(sortedOtherElements);
    
    return result;
}
//// Sort texts:

// Returns a sorted copy of the provided array of document list elements
// by the total score in corresponding topics
// (descending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTextScoreDesc(textElements) {
    if (lockTextsSorting){
	return sortElements(textElements, calculateTextScore, null, null);
    }
    else{
	return sortElements(textElements, calculateTextScore, compareValuesDesc, null);
    }
}


// Returns a sorted copy of the provided array of document list elements
// by the total score in corresponding topics
// (ascending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTextScoreAsc(textElements) {
    if (lockTextsSorting){
	return sortElements(textElements, calculateTextScore, null, null);
    }
    else{
	return sortElements(textElements, calculateTextScore, compareValuesAsc, null);
    }
}

// Returns a sorted copy of the provided array of document list elements
// by the total number of associated  themes
// (descending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTextThemesDesc(textElements) {
    if (lockTextsSorting){
	return sortElements(textElements, calculateTextThemesScore, null, null);
    }
    else{
	return sortElements(textElements, calculateTextThemesScore, compareValuesDesc, null);
    }
}

// Returns a sorted copy of the provided array of document list elements
// by the total number of associated  themes
// (descending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTextThemesAsc(textElements) {
    if (lockTextsSorting){
	return sortElements(textElements, calculateTextThemesScore, null, null);
    }
    else{
	return sortElements(textElements, calculateTextThemesScore, compareValuesAsc, null);
    }
}

// Returns a sorted copy of the provided array of document list elements
// by the name of the label
// (descending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTextLabelAsc(textElements) {
    if (lockTextsSorting){
	return sortElements(textElements, getLabelForSort, null, null);
    }
    else{
	return sortElements(textElements, getLabelForSort, compareStringValuesAsc, null);
    }
}

// Returns a sorted copy of the provided array of document list elements
// by the name of the label
// (descending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTextLabelDesc(textElements) {
    if (lockTextsSorting){
	return sortElements(textElements, getLabelForSort, null, null);
    }
    else{
	return sortElements(textElements, getLabelForSort, compareStringValuesDesc, null);
    }
}

//// Sort texts ends
 

// Returns a sorted copy of the provided array of topic list elements
// by the total score
// (descending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTopicScoreDesc(topicElements) {
    if (lockTopicsSorting){
	return sortElements(topicElements, calculateTopicScore, null, null);
    }
    else{
	return sortElements(topicElements, calculateTopicScore, compareValuesDesc, null);
    }
}

// Returns a sorted copy of the provided array of topic list elements
// by the total score
// (ascending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTopicScoreAsc(topicElements) {
    if (lockTopicsSorting){
	return sortElements(topicElements, calculateTopicScore, null, null);
    }
    else{
	return sortElements(topicElements, calculateTopicScore, compareValuesAsc, null);
    }
}


// Returns a sorted copy of the provided array of term list elements
// by the total score in corresponding topics
// (descending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTermsScoreDesc(termElements) {
    if (lockTermsSorting){
	return sortElements(termElements, calculateTermsScore, null, null);
    }
    else{
	return sortElements(termElements, calculateTermsScore, compareValuesDesc, null);
    }
}

// Returns a sorted copy of the provided array of term list elements
// by the total score in corresponding topics
// (ascending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTermsScoreAsc(termElements) {
      if (lockTermsSorting){
	return sortElements(termElements, calculateTermsScore, null, null);
    }
    else{
	return sortElements(termElements, calculateTermsScore, compareValuesAsc, null);
    }
}

// TODO: There is a lot of duplicated code for the sorting, this could be fixed
// Returns a sorted copy of the provided array of theme list elements
// by the time of creation
// (ascending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortThemesNumberofTextsAsc(themeElements) {
    return sortElements(themeElements, calculateThemesScore, compareNumberOfTextsAsc, compareValuesThemesRankingAscMachineLearning);
}

// TODO: There is a lot of duplicated code for the sorting, this could be fixed
// Returns a sorted copy of the provided array of theme list elements
// by the time of creation
// (ascending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortThemesNumberofTextsDesc(themeElements) {
    return sortElements(themeElements, calculateThemesScore, compareNumberOfTextsDesc, compareValuesThemesRankingAscMachineLearning);
}

// Returns a sorted copy of the provided array of theme list elements
// by the time of creation
// (ascending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortThemesTimeAsc(themeElements) {
    return sortElements(themeElements, calculateThemesScore, compareIdAsc, compareValuesThemesRankingAscMachineLearning);
}

// Returns a sorted copy of the provided array of theme list elements
// by the time of creation
// (descending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortThemesTimeDesc(themeElements) {
    return sortElements(themeElements, calculateThemesScore, compareIdDesc, compareValuesThemesRankingAscMachineLearning);
}

function isAssociatedSelectedForTerm(term) {
    let isRelatedTopicSelected = modelTopics.some(topic => isAssociatedTermTopic(term, topic.id) && currentTopicIds.has(topic.id))
    let isRelatedTextSelected = modelDocuments.some(([textId, text]) => isAssociatedTextTerm(text.id, term) && currentTextIds.has(text.id))
    let isRelatedThemeSelected = modelThemes.some(theme => isAssociatedThemeTerm(theme.id, term) && currentThemeIds.has(theme.id))

    return isRelatedTopicSelected || isRelatedTextSelected || isRelatedThemeSelected
}


// Calculates the total number of relevant topics for the provided array of term list elements
function calculateTermsTopicsNumber(termElements) {
    return $.map(termElements, function(element, i){
        let d = d3.select(element).datum();

        // Calculate the number
        let number = modelTermsToTopics.get(d.term)?.score_for_topics.size ?? 0

        // TODO: instead of simply using the count of topics,
        // check if the topics are filtered out, if this is necessary


        // The flag below is used to sort the selected elements separately
        // to ensure proper sorting for all sorting modes (desc/asc)
        let isSelected = isAssociatedSelectedForTerm(d.term);

        // Prepare the resulting element
        return { index: i, element: element, value: number, isSelected: isSelected };
    });
}

// Returns a sorted copy of the provided array of term list elements
// by the total number of corresponding topics
// (descending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTermsTopicsDesc(termElements) {
    return sortElements(termElements, calculateTermsTopicsNumber, compareValuesDesc, null);
	// Temporary array of element sorting values
}

// Returns a sorted copy of the provided array of term list elements
// by the total number of corresponding topics
// (ascending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTermsTopicsAsc(termElements) {
    return sortElements(termElements, calculateTermsTopicsNumber, compareValuesAsc, null);
}

// Calculates the total number of relevant documents for the provided array of term list elements
function calculateTermsDocsNumber(termElements) {
    return $.map(termElements, function(element, i){
        let d = d3.select(element).datum();

        // Calculate the number
        let number = modelTermsToDocuments.get(d.term)?.documents.size ?? 0;

        // The flag below is used to sort the selected elements separately
        // to ensure proper sorting for all sorting modes (desc/asc)
        let isSelected = isAssociatedSelectedForTerm(d.term);

        // Prepare the resulting element
        return { index: i, element: element, value: number, isSelected: isSelected};
    });
}

// Returns a sorted copy of the provided array of term list elements
// by the total number of corresponding documents
// (descending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTermsDocsDesc(termElements) {
    return sortElements(termElements, calculateTermsDocsNumber, compareValuesDesc, null);
}

// Returns a sorted copy of the provided array of term list elements
// by the total number of corresponding documents
// (ascending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTermsDocsAsc(termElements) {
    return sortElements(termElements, calculateTermsDocsNumber, compareValuesAsc, null);
}

// Provides a sorting value for term elements
function getTermStrings(termElements) {
    return $.map(termElements, function(element, i){
        let d = d3.select(element).datum();

        // The flag below is used to sort the selected elements separately
        // to ensure proper sorting for all sorting modes (desc/asc)
        let isSelected = isAssociatedSelectedForTerm(d.term);

        // Prepare the resulting element
        return { index: i, element: element, value: d.term, isSelected: isSelected};
    });
}

// Returns a sorted copy of the provided array of term list elements
// by the total number of corresponding documents
// (descending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTermsAlphaDesc(termElements) {
    return sortElements(termElements, getTermStrings, compareStringValuesDesc, null);
}

// Returns a sorted copy of the provided array of term list elements
// by the total number of corresponding documents
// (ascending order)
// Uses the mapping idea from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array/sort#Sorting_with_map
function sortTermsAlphaAsc(termElements) {
    return sortElements(termElements, getTermStrings, compareStringValuesAsc, null);
	// Temporary array of element sorting values
	let sortValues = getTermStrings(termElements);
	
}

///////
// Help functions for the highlighting
//////

function isAssociatedTermTopic(term, topicId) {
    return modelTermsToTopics.get(term)?.score_for_topics.has(topicId) ?? false
}

function isAssociatedTextTopic(textId, topicId) {
    return modelTopicsToDocuments.get(topicId)?.documents.has(textId) ?? false
}


function isAssociatedThemeTopic(themeId, topicId){
    if (!modelTopicsToDocuments.has(topicId) || !modelThemesToTexts.has(themeId)) {
        return false;
    }
    let themeTexts = modelThemesToTexts.get(themeId).texts;
    
    let modelTexts = modelTopicsToDocuments.get(topicId).documents;

    return modelTexts.some(text => themeTexts.has(text))
}

function isAssociatedThemeTerm(themeId, term) {
    if (!modelThemesToTexts.has(themeId)) {
        return false;
    }

    let themeTexts = modelThemesToTexts.get(themeId).texts;

    return themeTexts.some(textId => isAssociatedTextTerm(textId, term))
}

// Same as above, just to simpyfy the controller code
function isAssociatedTermTheme(term, themeId){
    return isAssociatedThemeTerm(themeId, term)
}

function isAssociatedTextTheme(textId, themeId) {
    return modelThemesToTexts.get(themeId)?.texts.has(textId) ?? false;
}

// Same as above, just to simpyfy the controller code
function isAssociatedThemeText(themeId, textId) {
    return isAssociatedTextTheme(textId, themeId);
}

function isAssociatedTextTerm(textId, term)
{
    return modelTermsToDocuments.get(term)?.documents.has(textId) ?? false;
}

// Same as above, just to simpyfy the controller code
function isAssociatedTermText(term, textId)
{
    return isAssociatedTextTerm(textId, term);
}


/////
// Setting and deleting selected items
/////
function modelToggleTermElement(termId){
    resetSelectedDataExcept(currentTermIds);
    toggleSelectedElements(termId, currentTermIds);
}

function modelToggleTopicElement(topicId){
    resetSelectedDataExcept(currentTopicIds);
    toggleSelectedElements(topicId, currentTopicIds);
}

function modelToggleTextElement(textId){
    let wasChosenBefore = false;
    if (currentTextIds.has(textId)) {
	wasChosenBefore = true;
    }
    resetSelectedDataExcept();
    if (!wasChosenBefore){
	currentTextIds.add(textId);
    }
    
	//    resetSelectedDataExcept(currentTextIds);
//    toggleSelectedElements(textId, currentTextIds);
}

function modelToggleThemeElement(themeId){    
    resetSelectedDataExcept(currentThemeIds);
    toggleSelectedElements(themeId, currentThemeIds);
}

function toggleSelectedElements(element, set){
    if (set.has(element)) {
	set.delete(element)
        return false;
    }
    else{
	set.add(element)
        return true;
    }
}

//////
// For determining if new models can be created
//////

async function modelCanModelBeCreated(){
    let canModelBeCreatedUrl = "can_model_be_created";
    let createModel = await get_data_async(canModelBeCreatedUrl, {});
    if (createModel == "False"){
	modelDisableModelCreation = 1; 
    }
}

//////
// For determining if analysis can be exported
//////

async function modelCanAnalysisBeExported(){
    let canAnalysisBeExportedUrl = "can_analysis_be_exported";
    modelAnalysisExportEnabled = await get_data_async(canAnalysisBeExportedUrl, {});
}

///////
/// For saving and fetching data from the manual analysis
////

/// Dataset
async function modelFillDataSetChoices(){
    let getDataChoicesUrl = "get_data_sets";
    modelDataSetChoices = [];
    let choices = await get_data_async(getDataChoicesUrl, {});

    modelDataSetChoices = choices.map(choice => ({"value" : choice}))
    
    modelDataSetChoices.push({"value" : SELECTDATASETTEXT})
}

async function modelGetDataSetChoices(){
    if(modelDataSetChoices == null){
        await modelFillDataSetChoices();
    }
    return modelDataSetChoices;
}

//////////////////////
// Save and fetch topic names
/////////////////////

async function modelRenameTopic(topicId, newLabel) {
    modelTopicNames.set(topicId, newLabel)
    
    let updateTopicNameUrl = "update_topic_name";
    let data = {"topic_id" : topicId, "topic_name" : newLabel, "analysis_id" : modelCurrentAnalysisVersionId};
    
    await save_data_async(updateTopicNameUrl, data);
}

async function getSavedTopicNames(){
    let savedTopicNamesUrl = "get_all_topic_names";
    let data = {"analysis_id" : modelCurrentAnalysisVersionId};

    let topic_names = await get_data_async(savedTopicNamesUrl, data);

    modelTopicNames = new Map(topic_names.map(topic_name => [topic_name.topic_id, topic_name.topic_name]))
}
    
function modelGetTopicNameForId(topic_id) {
    if (!modelTopicNames.has(topic_id)) {
        return undefined; // There is no user defined name for this topic
        // This part of the code is unneccssary, but keeping it for clairity
    }

    return modelTopicNames.get(topic_id)
}


async function deleteDatabaseTheme(themeId){
    let deleteThemeUrl = "delete_theme";
    let data = {"analysis_id": modelCurrentAnalysisVersionId, "theme_number": themeId};
    await save_data_async(deleteThemeUrl, data);
}


async function getSavedThemes(){
    let savedThemesUrl = "get_saved_themes";
    let data = {"analysis_id" : modelCurrentAnalysisVersionId};
    let themes = await get_data_async(savedThemesUrl, data);

    for (const theme of themes){
        let themeId = theme.theme_number;
        themeId = parseInt(themeId)
        let themeLabel = theme.theme_name
        addNewTheme(themeId, themeLabel);
    
        for (const textIdString of theme.document_ids){
            let textId = parseInt(textIdString)
            modelThemesToTexts.get(themeId).texts.add(textId)

	    // Also store the reverse connection
	    modelTextsToThemes
                .setdefault(textId, {"themes" : new Set()})
	        .themes.add(themeId)
        }
    }
}

async function modelRenameTheme(themeId, newLabel){
    let updateThemeNameUrl = "update_theme_name";
    let data = {"theme_number": themeId, "theme_name" : newLabel, "analysis_id" : modelCurrentAnalysisVersionId}
    
    await save_data_async(updateThemeNameUrl, data);
}


async function deleteDatabaseTextThemeLink(themeId, textId){
    let deleteDatabaseTextThemeLinkUrl = "delete_theme_document_connection";
    let data = {"theme_number" : themeId, "document_id" : textId, "analysis_id" : modelCurrentAnalysisVersionId};
    
    await save_data_async(deleteDatabaseTextThemeLinkUrl, data);
}

////////
/// For loading data in the scroll list of previous models and analyses
///////

async function modelLoadModelForSelectedDataSet(currentDataset){
    modelCurrentDataset = currentDataset;
    let modelForSelectedDataSetUrl = "get_all_models_for_collection_with_name";
    let data = {"collection_name" : currentDataset};
    
    let modelsForCurrentDatasetFromDataBase = await get_data_async(modelForSelectedDataSetUrl, data);
 
    resetModelData();
    resetModelChoiceData();
    
    for (const m of modelsForCurrentDatasetFromDataBase) {
        var  name_to_use = m["model_name"] + " " + m["date"];
        modelModelsForCurrentDataset.push({"value" : name_to_use, "id" : m["_id"]});
    }
    
    modelModelsForCurrentDataset.push({"value" : SELECTMODELTEXT, "id" : undefined});
}

///////
/// For constructing a new model
async function modelConstructNewModel(modelName){
    let contructNewModelUrl = "make_model_for_collection";
    let data = {"collection_name" : modelCurrentDataset, "model_name" : modelName};
    let result = await save_data_async(contructNewModelUrl, data);
    await modelLoadModelForSelectedDataSet(modelCurrentDataset);
    return result.id;
}


///For loading the analyses-list
async function modelLoadAnalysesForSelectedModel(newModelId){
    modelCurrentModelId = newModelId;
    return modelLoadAnalysis();
}

async function modelLoadAnalysis(){
    let loadAnalysesUrl = "get_all_analyses_for_model";
    let data = {"model_id" : modelCurrentModelId};
    resetUserAnalysisData();
    
    let analysesForCurrentModelFromDataBase = await get_data_async(loadAnalysesUrl, data);

    resetAnalysisChoiceData();
    for (const m of analysesForCurrentModelFromDataBase) {
        modelAnalysesForCurrentModel.push({"value" : m["analysis_name"], "id" : m["_id"]});
    }
    
    modelAnalysesForCurrentModel.push({"value" : SELECTANALYSISTEXT, "id" : undefined});
}



async function modelLoadNewAnalysis(newAnalysisVersionId){
    resetUserAnalysisData();
    modelCurrentAnalysisVersionId = newAnalysisVersionId;

    return Promise.all([
	getSavedTopicNames(),
	getSavedUserDefinedLabels(),
	getSavedThemes()
    ]);
}

///////
/// For constructing a new analysis, loading analyses and exporting analysis
////////////
async function modelConstructNewAnalysis(analysisName){
    let constructNewAnalysisUrl = "create_new_analysis";
    let data = {"model_id" : modelCurrentModelId, "analysis_name" : analysisName};
    let createdAnalysisParameters = await save_data_async(constructNewAnalysisUrl, data);

    let modelCurrentAnalysisName = createdAnalysisParameters["analysis_name"];
    modelCurrentAnalysisVersionId = createdAnalysisParameters["analysis_id"];
    console.log("modelLoadAnalysisForCurrentModel", modelCurrentAnalysisName);

    await modelLoadAnalysis();
    return modelCurrentAnalysisName;
}

async function modelExportAnalysis() {
    if (modelCurrentAnalysisVersionId == null){
	// Nothing to export if there is no analysis
	return;
    }
    let exportAnalysisUrl = "export_analysis";
    let data = {"analysis_id" : modelCurrentAnalysisVersionId};
    await save_data_async(exportAnalysisUrl, data);
    alert("Saved analysis with id: " + savedData["analysis_id"] + ".\nTo folder: " +savedData["data_dir"]);
}



/////////////////////////////////////////
/// Handling user defined text labels
/////////////////////////////////////

function modelGetTextLabelForId(textId){
    if (modelUserTextLabels[textId] == undefined){
        return undefined;
    }
    return modelUserTextLabels[textId]
}

function modelDefineUserLabel(textId, userDefinedLabel){
    modelUserTextLabels[textId] = userDefinedLabel;
    
    let updateUserLabelUrl = "update_user_defined_label";
    let data = {"text_id" : textId, "user_defined_label" : userDefinedLabel, "analysis_id" : modelCurrentAnalysisVersionId};
    
    return save_data_async(updateUserLabelUrl, data);
}

async function getSavedUserDefinedLabels(){
    let savedUserDefinedLabels = "get_all_user_defined_labels";
    let data = {"analysis_id" : modelCurrentAnalysisVersionId};
    
    let userLabels = await get_data_async(savedUserDefinedLabels, data);

    for (const userLabel of userLabels){
        modelUserTextLabels[userLabel.text_id] = userLabel.user_defined_label;
    }
}

function modelResetRecentlyClickedForMachineLearningSorting(){
    modelMostRecentlyClickedText = undefined;
    modelThemeRankingForMostRecentlyClickedText = [];
}

