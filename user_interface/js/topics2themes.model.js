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
var currentTermIds = [];
// The topics that are selected
var currentTopicIds = [];
// The documents that are selected
var currentTextIds = [];
// The themes that are selected
var currentThemeIds = [];

// Used for sorting the themes that are not currently selected
var modelMostRecentlyClickedText;
var modelThemeRankingForMostRecentlyClickedText = [];

var modelShowArgumentation = undefined;

var modelShowSentiment = undefined;

var modelDisableModelCreation = undefined;

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

// Document timestamp comparator
function compareDocumentTimestampAsc(a, b){
	let datumA = d3.select(a).datum();
	let datumB = d3.select(b).datum();
	
	let timestampA = moment(datumA.timestamp, 'dd MMM DD HH:mm:ss ZZ YYYY');
	let timestampB = moment(datumB.timestamp, 'dd MMM DD HH:mm:ss ZZ YYYY');
	
	return timestampA - timestampB;
}

// Document timestamp comparator
function compareDocumentTimestampDesc(a, b){
	let datumA = d3.select(a).datum();
	let datumB = d3.select(b).datum();
	
	let timestampA = moment(datumA.timestamp, 'dd MMM DD HH:mm:ss ZZ YYYY');
	let timestampB = moment(datumB.timestamp, 'dd MMM DD HH:mm:ss ZZ YYYY');
	
	return timestampB - timestampA;
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
    modelTermsToTopics = {};
    modelTermsToDocuments = {};
    modelTopicsToDocuments = {};
    modelTopics = [];
    modelDocuments = [];
    modelLabelCategories = [];
    resetSelectedDataExcept();
    resetUserAnalysisData();
    resetAnalysisChoiceData();

}

function resetUserAnalysisData(){
    modelThemes = [];
    modelThemesToTexts = {};
    modelTextsToThemes = {};
    modelTopicNames = {};
    modelUserTextLabels = {};
    
    modelResetRecentlyClickedForMachineLearningSorting();
    modelResetClickedChoices();
}

function modelResetClickedChoices(){
    currentTermIds = [];
    currentTopicIds = [];
    currentTextIds = [];
    currentThemeIds = [];
}

// Resets all list of selected items, except the argument (if such an argument is submitted)
function resetSelectedDataExcept(notToReset){
    if (notToReset != currentTermIds){
        currentTermIds = [];
    }
    
    if (notToReset != currentTopicIds){
        currentTopicIds = [];

    }
    
    if (notToReset != currentTextIds){
        currentTextIds = [];
    }
    
    if (notToReset != currentThemeIds){
        currentThemeIds = [];
    }
}

function modelCreateNewTheme(){
    if (modelCurrentAnalysisVersionId == null){
	// Don't create new themes if no analysis has been selected
	return;
    }
    let createThemeUrl = "create_new_theme";
    let data = {"analysis_id" : modelCurrentAnalysisVersionId};
    save_data(createThemeUrl, doCreateNewTheme, data);
}

function doCreateNewTheme(themeId){
    addNewTheme(themeId, "");
    controllerDoPopulateThemes(true);  // do default sorting
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
    
    modelThemesToTexts[themeId] = {
        "texts" : []
    }
}

/////////
// General functionality used for communicating with server
///////

function get_data(url, success_function, dataToSend) {
    dataToSend["authentication_key"] = authenticationKey
    $.ajax({url:BASEURL + url, dataType: "json",
       data: dataToSend,
       type: "GET",
       success: function(json, status) {
       success_function(json["result"]);
       },
       error: function(xhr,status,error) {
       alert("Something went wrong with " + url + " " + error)
       }
       });
}

function save_data(url, success_function, dataToSend) {
    dataToSend["authentication_key"] = authenticationKey
    $.ajax({url:BASEURL + url, dataType: "json",
           data: dataToSend,
           type: "POST",
           success: function(json, status) {
           success_function(json["result"]);
           },
           error: function(xhr,status,error) {
           alert("Something went wrong with " + url + " " + error)
           }
           });
}


	
// Initializes the data entries
function modelInitializeData(modelId) {
    modelCurrentModelId = modelId;
    get_data("get_model_for_model_id", doInitializeData, {"model_id" : modelId});
  
}

function doInitializeData(res){
    resetModelData()
    jsonData = res["topic_model_output"];
    let documents = jsonData.documents;
	let topics = jsonData.topics;
    
    let labelCategories = jsonData["meta_data"]["configuration"]["DATA_LABEL_LIST"]
    modelLabelCategories = [];
    for (let index = 0; index < labelCategories.length; index++)
    {
        var color = "silver";
        if ("label_color" in labelCategories[index]){
            color = labelCategories[index]["label_color"]
        }
        modelLabelCategories.push({"label" : labelCategories[index]["data_label"], "color" : color})
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
    for (let i = 0; i < topics.length; i++) {
	let topic = topics[i];

        modelTopics.push({"id" : topic.id, "defaultlabel" : topic.label})
	
        if (topic.topic_terms == undefined){
            alert("Terms missing for topic number  " +  topic.id);
			continue;
        }

        for (let j = 0; j < topic.topic_terms.length; j++) {
			let topic_term = topic.topic_terms[j];
			if (modelTermsToTopics[topic_term.term] == undefined) {
				modelTermsToTopics[topic_term.term] = {
					"term": topic_term.term,
					"topics": [],
                    "score_for_topics": []
				};
            }
			modelTermsToTopics[topic_term.term].topics.push(topic.id);
            modelTermsToTopics[topic_term.term].score_for_topics.push(topic_term.score);
 		}
    
	}
    
	// Extract the array of values from the dictionary
	modelTerms = Object.values(modelTermsToTopics);
    
	// Establish the reverse mappings from topics to documents and terms to documents
	modelTopicsToDocuments = {};
	modelTermsToDocuments = {};
	
	for (let i = 0; i < documents.length; i++) {
		// NOTE: "document" is a pretty important DOM object,
		// so better use other local variable names
	    var doc = documents[i];
  


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
            modelDocuments.push({"id" : doc.id, "text" : doc.text, "label": doc.label, "marked_text_tok": doc.marked_text_tok, "additional_labels" : doc.additional_labels, "snippet": snippet, "base_name" : doc.base_name})
		
		if (doc.document_topics == undefined)
			continue;
		
		for (let j = 0; j < doc.document_topics.length; j++){
			let doc_topic = doc.document_topics[j];
			if (modelTopicsToDocuments[doc_topic.topic_index] == undefined) {
				modelTopicsToDocuments[doc_topic.topic_index] = {
					"topic": doc_topic.topic_index,
					"documents": [],
                    "topic_confidences" : []
				};
			}
			modelTopicsToDocuments[doc_topic.topic_index].documents.push(doc.id);

            modelTopicsToDocuments[doc_topic.topic_index].topic_confidences.push(doc_topic.topic_confidence);
			
			for (let k = 0; k < doc_topic.terms_in_topic.length; k++) {
				let doc_term = doc_topic.terms_in_topic[k];
				if (modelTermsToDocuments[doc_term.term] == undefined) {
					modelTermsToDocuments[doc_term.term] = {
						"term": doc_term,
						"documents": []
					};
				}
				modelTermsToDocuments[doc_term.term].documents.push(doc.id)
			}
		}
	}
    
    controllerDoPopulateInterface();
}


function getScoreForTermTopic(term, topicId){
    let topicIndex = modelTermsToTopics[term].topics.indexOf(topicId);
    if (topicIndex != -1){
        return modelTermsToTopics[term].score_for_topics[topicIndex];
    }
    else{
        return undefined;
    }
}

// TODO: Implement this as a dictionary instead. If the list of text gets long, this might be slow?
function getLabelForText(textId){
    for (let j = 0; j < modelDocuments.length; j++){
        if (modelDocuments[j].id == textId){
            let label = modelGetTextLabelForId(modelDocuments[j].id);
            if (label == undefined){ // No user label, use automatic label
                label = modelDocuments[j].label;
            }
            return label;
        }
    }
    return undefined;
}

// TODO: Implement this as a dictionary instead. If the list of text gets long, this might be slow?
function getAdditionalLabelsForText(textId){
    for (let j = 0; j < modelDocuments.length; j++){
        if (modelDocuments[j].id == textId){
            return modelDocuments[j].additional_labels.sort();
        }
    }
    return undefined;
}

////
// For getting the maximum score for the four categories (used for sorting)
////
function getMaxTermScore(){
    let all_scores = [];
    $.each(modelTermsToTopics, function(k, v){
            all_scores = all_scores.concat(v.score_for_topics)
           });
    return _.max(all_scores)
}

// Get the maximum creation data
function getMaxThemeScore(){
    let all_scores = [];
    
    for (let j = 0; j < modelThemes.length; j++ ){
        all_scores = all_scores.concat(modelThemes[j].creation_time);
    }
    return _.max(all_scores)
}

function getMaxTopicScore(){
    let all_scores = [];
    for (let j = 0; j < modelTopics.length; j++ ){
        let topicId = modelTopics[j].id
        let tot_score = 0
    // Let the score of a topic be the total score for the terms that belong to it
    // TODO: This code is duplicated, make a function
        $.each(modelTermsToTopics, function(k, v){
           let topic_index = v.topics.indexOf(topicId);
           if (topic_index > -1)
           tot_score = tot_score  + v.score_for_topics[topic_index]
           });
        all_scores = all_scores.concat(tot_score)
    }
    return _.max(all_scores)

}

function getMaxDocumentScore(){
    var maxScore = 0;
    $.each(modelTopicsToDocuments, function(key, topicsToDocumentsValue){
        for (var j = 0; j < topicsToDocumentsValue.topic_confidences.length; j++){
            if (topicsToDocumentsValue.topic_confidences[j] > maxScore){
                maxScore = topicsToDocumentsValue.topic_confidences[j];
           }
           }
           });
    return maxScore;    
}



function modelAddTextThemeLink(themeId, textId){

    if (modelThemesToTexts[themeId].texts.indexOf(textId) == -1){
        modelThemesToTexts[themeId].texts.push(textId)
    }

    if (!(textId in modelTextsToThemes)){
	// For storing connections between texts and themes
	modelTextsToThemes[textId] = {"themes" : []};
    }

    if (modelTextsToThemes[textId].themes.indexOf(themeId) == -1){
        modelTextsToThemes[textId].themes.push(themeId)
    }
    
    let addTextThemeLinkUrl = "add_theme_document_connection";
    let data = {"theme_number" :themeId,
        "document_id":textId, "analysis_id": modelCurrentAnalysisVersionId};
    
    save_data(addTextThemeLinkUrl, doAddTextThemeLink, data);
}

function doAddTextThemeLink(res){
    // not used, only kept for debug purposes
}

function hasThemeAssociatedTexts(themeId){
    if (modelThemesToTexts[themeId] != undefined){
        if (modelThemesToTexts[themeId].texts.length > 0){
            return true;         }
    }
    return false;
}


function removeTheme(themeId){
    if (hasThemeAssociatedTexts(themeId)){
        return false; // It is not allowed to delete themes that have associated texts.

    }
    let index = modelThemes.findIndex(function(e){ return e.id == themeId; });
    if (index < 0)
    	return false;

    modelThemes.splice(index, 1);
    delete modelThemesToTexts[themeId];
    
    deleteDatabaseTheme(themeId)
    // Reset all selections when a theme is removed
    resetSelectedDataExcept();
    
    return true;
}

function removeTextThemeLink(themeId, textId){
    let indexToRemove = modelThemesToTexts[themeId].texts.indexOf(textId);
    modelThemesToTexts[themeId].texts.splice(indexToRemove, 1);
    
    let themeIndexToRemove = modelTextsToThemes[textId].themes.indexOf(themeId);
    modelTextsToThemes[textId].themes.splice(themeIndexToRemove, 1);

    deleteDatabaseTextThemeLink(themeId, textId);
}


function modelSetMostRecentlyClickedForThemeRanking(textId){
    // TODO: Chosing not to sort after it already has been sorted doesn't seem to work
    if (currentTextIds.indexOf(textId) == -1 || modelCurrentAnalysisVersionId == null || !doThemesSorting){
        // Then it was an unclick a previously selected text
        if (currentTextIds.length == 0){
            // If no more documents are selected, reset the machine learning based theme sorting
            modelResetRecentlyClickedForMachineLearningSorting();
        }
        if (!doThemesSorting && currentTextIds.indexOf(textId) != -1){
            modelMostRecentlyClickedText = textId; // Save to use for later if doThemesSorting would be enabled
        }
        
        return;
    }
    //else:
    modelMostRecentlyClickedText = textId; // Used for sorting the themes that are not currently selected
}


function modelSortThemesWithMachineLearningIfTextChosen(){
    if(modelMostRecentlyClickedText == undefined){
        sortThemesList(themeSortMode);
        renderLinks();
    }
    else{
        let themeRankingUrl = "get_theme_ranking_for_document";
        let data = {"document_id" : modelMostRecentlyClickedText, "analysis_id" : modelCurrentAnalysisVersionId};
    
        get_data(themeRankingUrl, resortThemes, data);
    }
}

// Called via callback from modelSortThemesWithMachineLearningIfTextChosen
function resortThemes(themeSorting){
    modelThemeRankingForMostRecentlyClickedText = themeSorting;
    sortThemesList(themeSortMode);
    renderLinks();
}




// Calculates the total score for the provided array of term list elements
function calculateTermsScore(termElements) {
	return $.map(termElements, function(element, i){
		let d = d3.select(element).datum();
		
		let accScore = 0;

		// The flag below is used to sort the selected elements separately
		// to ensure proper sorting for all sorting modes (desc/asc)
		let isSelected = false;

        for (let i = 0; i < currentTopicIds.length; i++){
            if (isAssociatedTermTopic(d.term, currentTopicIds[i])){
                    accScore = accScore + getScoreForTermTopic(d.term, currentTopicIds[i]);
                    isSelected = true;
                 }
        }
                 
        if (!isSelected){
                 for (let j = 0; j < modelTopics.length; j++ ){
                 let topic = modelTopics[j];
                 if (isAssociatedTermTopic(d.term, topic.id)){
                 // This is the standard score to give to the term, an
                 // accumulation of each topic it
                 // is associated to, if no topic is chosen
                 
                 accScore = accScore + getScoreForTermTopic(d.term, topic.id);
                 }}}
                 
		for (let j = 0; j < currentTextIds.length; j++ ){
			let text = currentTextIds[j];
			if (isAssociatedTextTerm(text, d.term)){
                isSelected = true;
			}
		}

		for (let j = 0; j < currentThemeIds.length; j++ ){
			let theme = currentThemeIds[j];
			if (isAssociatedThemeTerm(theme, d.term)){
					isSelected = true;
			}
		}
		// Prepare the resulting element
        return { index: i, element: element, value: accScore, isSelected: isSelected, secondaryValue: d.term.length};
	});
}


// Calculates the total score for the provided array of text list elements
function calculateTextScore(textElements) {
    return $.map(textElements, function(element, i){
            let d = d3.select(element).datum();
            let accScore = 0;
            
            // The flag below is used to sort the selected elements separately
    		// to ensure proper sorting for all sorting modes (desc/asc)
    		let isSelected = false;
                 
            for (let i = 0; i < currentTopicIds.length; i++){
                 if (isAssociatedTextTopic(d.id, currentTopicIds[i])){
                 // TODO: Strange structure in modelTopicsToDocuments makes this code a bit strange, should restructure
                    let textIndexIn_ModelTopicsToDocuments = modelTopicsToDocuments[currentTopicIds[i]].documents.indexOf(d.id);
                    let topicConfidence = modelTopicsToDocuments[currentTopicIds[i]].topic_confidences[textIndexIn_ModelTopicsToDocuments];
                    accScore = accScore + topicConfidence;
                    isSelected = true;
                 }
                 }
            ///
    
            if (!isSelected){
                 let scores = []
                 for (let j = 0; j < modelTopics.length; j++ ){
                    let topic = modelTopics[j];
                    if (isAssociatedTextTopic(d.id, topic.id)){
                 // This is the standard score to give to the term, an
                 // accumulation of each topic it
                 // is associated to, if no topic is chosen
                 // TODO: Strange structure in modelTopicsToDocuments makes this code a bit strange, should restructure
                    let textIndexIn_ModelTopicsToDocuments = modelTopicsToDocuments[topic.id].documents.indexOf(d.id);
                    let topicConfidence = modelTopicsToDocuments[topic.id].topic_confidences[textIndexIn_ModelTopicsToDocuments];
                    scores.push(topicConfidence)
                    accScore = accScore + topicConfidence;
                 }}
                 // When no topic is chosen, use the mean strength for the topics
                 for (let k = 0; k < scores.length; k++){
                    accScore = accScore + scores[k];
                 }
                 accScore = accScore/scores.length;
                 }
    
            for (let j = 0; j < currentTermIds.length; j++ ){
                let term = currentTermIds[j];
                if (isAssociatedTextTerm(d.id, term)){
                    isSelected = true;
                 }}
                 
            for (let j = 0; j < currentThemeIds.length; j++ ){
                let theme = currentThemeIds[j];
                 
                if (isAssociatedTextTheme(d.id, theme)){
                    isSelected = true;
                 }}

            // Prepare the resulting element
                 // If the association score is the same, sort according to inverse document length, as a short document with high association should have a higher expressiveness
                 return { index: i, element: element, value: accScore, isSelected: isSelected, secondaryValue: -1*d.text.length};
      });
    
}


function calculateTextThemesScore(textElements) {
	return $.map(textElements, function(element, i){

	    let number = 0;
	    let d = d3.select(element).datum();
	    if (d.id in modelTextsToThemes){
		number = modelTextsToThemes[d.id].themes.length;
	     }
	   
	    // The flag below is used to sort the selected elements separately
	    // to ensure proper sorting for all sorting modes (desc/asc)
	    let isSelected = false;

	    for (let j = 0; j < modelTopics.length; j++ ){
		let topic = modelTopics[j];
		if (isAssociatedTextTopic(d.id, topic.id)){
				if (currentTopicIds.indexOf(topic.id) > -1){
					isSelected = true;
				}
			}
		}

		for (let j = 0; j < modelTerms.length; j++ ){
			let term = modelTerms[j];
			if (isAssociatedTextTerm(d.id, term.term)){
				if (currentTermIds.indexOf(term.term) > -1){
					isSelected = true;
				}
			}
		}

		for (let j = 0; j < modelThemes.length; j++ ){
			let theme = modelThemes[j];
			if (isAssociatedTextTheme(d.id, theme.id)){
				if (currentThemeIds.indexOf(theme.id) > -1){
					isSelected = true;
				}
			}
		}
				
		// Prepare the resulting element
		return { index: i, element: element, value: number, isSelected: isSelected};
	});
}


function getLabelForSort(textElements) {
	return $.map(textElements, function(element, i){

	    let d = d3.select(element).datum();
	    let label = d.label;

	    if (d.id in modelUserTextLabels){
		label = modelUserTextLabels[d.id]
	    }

	    // The flag below is used to sort the selected elements separately
	    // to ensure proper sorting for all sorting modes (desc/asc)
	    let isSelected = false;

	    for (let j = 0; j < modelTopics.length; j++ ){
		let topic = modelTopics[j];
		if (isAssociatedTextTopic(d.id, topic.id)){
				if (currentTopicIds.indexOf(topic.id) > -1){
					isSelected = true;
				}
			}
		}

		for (let j = 0; j < modelTerms.length; j++ ){
			let term = modelTerms[j];
			if (isAssociatedTextTerm(d.id, term.term)){
				if (currentTermIds.indexOf(term.term) > -1){
					isSelected = true;
				}
			}
		}

		for (let j = 0; j < modelThemes.length; j++ ){
			let theme = modelThemes[j];
			if (isAssociatedTextTheme(d.id, theme.id)){
				if (currentThemeIds.indexOf(theme.id) > -1){
					isSelected = true;
				}
			}
		}
				
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

                // The flag below is used to sort the selected elements separately
         	// to ensure proper sorting for all sorting modes (desc/asc)
                 let isSelected = false;
 

         		
                 
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
                 let textScores = [];
                 $.each(modelTopicsToDocuments, function(k, v){
                        let document_index = v.documents.indexOf(d.id);
                        if (document_index > -1){
                        textScores.push(v.topic_confidences[document_index]);
                        }
                });
                let totTextScore = 0;
                for (let j = 0; j < textScores.length; j++){
                    totTextScore = totTextScore + textScores[j];
                }
                let finalTextScore = totTextScore/textScores.length;
                 
                // Check if term is selected
                for (let j = 0; j < currentTermIds.length; j++ ){
                    let term = currentTermIds[j];
        
                    if (isAssociatedTermTopic(term, d.id)){
                            isSelected = true;
                    }
                 }
                 
                 for (let j = 0; j < currentTextIds.length; j++ ){
                    let text = currentTextIds[j];
                    if (isAssociatedTextTopic(text, d.id)){
                        isSelected = true;
                 }}
   
                 for (let j = 0; j < currentThemeIds.length; j++ ){
                    let theme = currentThemeIds[j];
                 
                    if (isAssociatedThemeTopic(theme, d.id)){
                        isSelected = true;
                 }}
                 
                
                 return { index: i, element: element, value: finalTextScore, isSelected: isSelected};
       });
    
}


// Calculates the total score for the provided array of text list elements
function calculateThemesScore(themeElements) {
    return $.map(themeElements, function(element, i){
                 let d = d3.select(element).datum();
                 // Use creation time to dedice how to sort
                 let tot_score = d.creation_time;
                 
                 // The flag below is used to sort the selected elements separately
          		 // to ensure proper sorting for all sorting modes (desc/asc)
          		 let isSelected = false;
                 
                 for (let j = 0; j < currentTopicIds.length; j++ ){
                    let topic = currentTopicIds[j];
                    if (isAssociatedThemeTopic(d.id, topic)){
                            isSelected = true;
                 }}
                 
                 for (let j = 0; j < currentTermIds.length; j++ ){
                    let term = currentTermIds[j];
                    if (isAssociatedThemeTerm(d.id, term)){
                        isSelected = true;
                 }}
                 
                 for (let j = 0; j < currentTextIds.length; j++ ){
                    let text = currentTextIds[j];
                    if (isAssociatedTextTheme(text, d.id)){
                        isSelected = true;
                 }}
                 
                 let numberOfAssociateTexts = modelThemesToTexts[d["id"]].texts.length;
               
                 return { index: i, element: element, value: tot_score, isSelected: isSelected, id: d["id"], numberOfTexts: numberOfAssociateTexts };
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

// Calculates the total number of relevant topics for the provided array of term list elements
function calculateTermsTopicsNumber(termElements) {
	return $.map(termElements, function(element, i){
		let d = d3.select(element).datum();
		
		// Calculate the number
		let number = 0;
		if (d.term in modelTermsToTopics) {
			number = modelTermsToTopics[d.term].topics.length;
		}
		
		// TODO: instead of simply using the count of topics,
		// check if the topics are filtered out, if this is necessary
		
		
		// The flag below is used to sort the selected elements separately
		// to ensure proper sorting for all sorting modes (desc/asc)
		let isSelected = false;

		for (let j = 0; j < modelTopics.length; j++ ){
			let topic = modelTopics[j];
			if (isAssociatedTermTopic(d.term, topic.id)){
				if (currentTopicIds.indexOf(topic.id) > -1){
					isSelected = true;
				}
			}
		}

		for (let j = 0; j < modelDocuments.length; j++ ){
			let text = modelDocuments[j];
			if (isAssociatedTextTerm(text.id, d.term)){
				if (currentTextIds.indexOf(text.id) > -1){
					isSelected = true;
				}
			}
		}

		for (let j = 0; j < modelThemes.length; j++ ){
			let theme = modelThemes[j];
			if (isAssociatedThemeTerm(theme.id, d.term)){
				if (currentThemeIds.indexOf(theme.id) > -1){
					isSelected = true;
				}
			}
		}
				
		// Prepare the resulting element
		return { index: i, element: element, value: number, isSelected: isSelected};
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
		let number = 0;
		if (d.term in modelTermsToDocuments) {
			number = modelTermsToDocuments[d.term].documents.length;
		}
		
		// The flag below is used to sort the selected elements separately
		// to ensure proper sorting for all sorting modes (desc/asc)
		let isSelected = false;

		for (let j = 0; j < modelTopics.length; j++ ){
			let topic = modelTopics[j];
			if (isAssociatedTermTopic(d.term, topic.id)){
				if (currentTopicIds.indexOf(topic.id) > -1){
					isSelected = true;
				}
			}
		}

		for (let j = 0; j < modelDocuments.length; j++ ){
			let text = modelDocuments[j];
			if (isAssociatedTextTerm(text.id, d.term)){
				if (currentTextIds.indexOf(text.id) > -1){
					isSelected = true;
				}
			}
		}

		for (let j = 0; j < modelThemes.length; j++ ){
			let theme = modelThemes[j];
			if (isAssociatedThemeTerm(theme.id, d.term)){
				if (currentThemeIds.indexOf(theme.id) > -1){
					isSelected = true;
				}
			}
		}
		
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
		let isSelected = false;

		for (let j = 0; j < modelTopics.length; j++ ){
			let topic = modelTopics[j];
			if (isAssociatedTermTopic(d.term, topic.id)){
				if (currentTopicIds.indexOf(topic.id) > -1){
					isSelected = true;
				}
			}
		}

		for (let j = 0; j < modelDocuments.length; j++ ){
			let text = modelDocuments[j];
			if (isAssociatedTextTerm(text.id, d.term)){
				if (currentTextIds.indexOf(text.id) > -1){
					isSelected = true;
				}
			}
		}

		for (let j = 0; j < modelThemes.length; j++ ){
			let theme = modelThemes[j];
			if (isAssociatedThemeTerm(theme.id, d.term)){
				if (currentThemeIds.indexOf(theme.id) > -1){
					isSelected = true;
				}
			}
		}
		
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

function isAssociatedTermTopic(term, topicId){
    return (modelTermsToTopics[term] != undefined
            && modelTermsToTopics[term].topics.indexOf(topicId) > -1);
}

function isAssociatedTextTopic(textId, topicId){
    return (modelTopicsToDocuments[topicId] != undefined
            && modelTopicsToDocuments[topicId].documents.indexOf(textId) > -1);
}


function isAssociatedThemeTopic(themeId, topicId){
    if (modelTopicsToDocuments[topicId] == undefined || modelThemesToTexts[themeId] == undefined){
        return false;
    }
    let themeTexts = modelThemesToTexts[themeId].texts;
    
    let modelTexts = modelTopicsToDocuments[topicId].documents;
    for (var i = 0; i < modelTexts.length; i++){
        if(themeTexts.indexOf(modelTexts[i]) > -1){
            return true;
        }
    }
    return false;
}

function isAssociatedThemeTerm(themeId, term){
    if (modelThemesToTexts[themeId] == undefined){
        return false;
    }

    let themeTexts = modelThemesToTexts[themeId].texts;
    
    for (var i = 0; i < themeTexts.length; i++){
        let loopTextId = themeTexts[i];
        if (isAssociatedTextTerm(loopTextId, term)){
            return true;
            }
    }
    return false;
}

// Same as above, just to simpyfy the controller code
function isAssociatedTermTheme(term, themeId){
    return isAssociatedThemeTerm(themeId, term)
}

function isAssociatedTextTheme(textId, themeId){
    let associated = modelThemesToTexts[themeId] != undefined
    && modelThemesToTexts[themeId].texts.indexOf(textId) > -1;

    return associated;
}

// Same as above, just to simpyfy the controller code
function isAssociatedThemeText(themeId, textId){
    return isAssociatedTextTheme(textId, themeId);
}

function isAssociatedTextTerm(textId, term)
{
    return (modelTermsToDocuments[term] != undefined
            && modelTermsToDocuments[term].documents.indexOf(textId) > -1);
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
    resetSelectedDataExcept(currentTextIds);
    toggleSelectedElements(textId, currentTextIds);
}

function modelToggleThemeElement(themeId){
    resetSelectedDataExcept(currentThemeIds);
    toggleSelectedElements(themeId, currentThemeIds);
}

// Help function for adding and removing selected elements
function toggleSelectedElements(element, list){
    if (list.indexOf(element) > -1) {
        list.splice(list.indexOf(element), 1);
        return false;
    }
    else{
        list.push(element);
        return true;
    }
}

//////
// For determining if new models can be created
//////

function modelCanModelBeCreated(){
    let canModelBeCreatedUrl = "can_model_be_created";
    get_data(canModelBeCreatedUrl, modelSetCanModelBeCreated, {});
}


function modelSetCanModelBeCreated(createModel){
    if (createModel == "False"){
	modelDisableModelCreation = 1; 
    }
}

///////
/// For saving and fetching data from the manual analysis
////

/// Dataset
function modelFillDataSetChoices(){
    let getDataChoicesUrl = "get_data_sets";
    modelDataSetChoices = [];
    get_data(getDataChoicesUrl, modelDoFillDataSetChoices, {});
}

function modelDoFillDataSetChoices(choices){
    for (let i = 0; i < choices.length; i++) {
        var choice = choices[i];
        modelDataSetChoices.push({"value" : choice})
    }
    
    modelDataSetChoices.push({"value" : SELECTDATASETTEXT})
    
    controllerDoPopulateDataChoices(modelDataSetChoices);
}

function modelGetDataSetChoices(){
    if(modelDataSetChoices == null){
        modelFillDataSetChoices();
    }
    else{
    controllerDoPopulateDataChoices(modelDataSetChoices);
    }
}

//////////////////////
// Save and fetch topic names
/////////////////////

function modelRenameTopic(topicId, newLabel){
    modelTopicNames[topicId] = newLabel;
    
    let updateTopicNameUrl = "update_topic_name";
    let data = {"topic_id" : topicId, "topic_name" : newLabel, "analysis_id" : modelCurrentAnalysisVersionId};
    
    save_data(updateTopicNameUrl, updateTopicNameList, data);
}

function updateTopicNameList(dummy){
     // Dont use this at the moment
}

function getSavedTopicNames(){
    let savedTopicNamesUrl = "get_all_topic_names";
    let data = {"analysis_id" : modelCurrentAnalysisVersionId};

    get_data(savedTopicNamesUrl, doGetSavedTopicNames, data);
}



function doGetSavedTopicNames(topic_names){
   
    for (let i = 0; i < topic_names.length; i++){
        modelTopicNames[topic_names[i].topic_id] = topic_names[i].topic_name;
    }
    // TODO: Perhaps this shouldn't be done here, but later, or split up into subfunctions
    controllerDoPopulateTopicElements();
}
    
function modelGetTopicNameForId(topic_id){
    if (modelTopicNames[topic_id] == undefined){
	return undefined; // There is no user defined name for this topic
        // This part of the code is unneccssary, but keeping it for clairity
    }
    return modelTopicNames[topic_id]
    
}


function deleteDatabaseTheme(themeId){
    let deleteThemeUrl = "delete_theme";
    let data = {"analysis_id": modelCurrentAnalysisVersionId, "theme_number": themeId};
    save_data(deleteThemeUrl, doDeleteDatabaseTheme, data);
}

function doDeleteDatabaseTheme(res){
    // Not used at the moment
    //(res);
}


function getSavedThemes(){
    let savedThemesUrl = "get_saved_themes";
    let data = {"analysis_id" : modelCurrentAnalysisVersionId};
    get_data(savedThemesUrl, doGetSavedThemes, data);
}


function doGetSavedThemes(themes){
    for (let i = 0; i < themes.length; i++){
        let themeId = themes[i].theme_number;
        themeId = parseInt(themeId)
        let themeLabel = themes[i].theme_name
        addNewTheme(themeId, themeLabel);
    
        for (let j = 0; j < themes[i].document_ids.length; j++){
            let textId = themes[i].document_ids[j];
            textId = parseInt(textId)
            if (modelThemesToTexts[themeId].texts.indexOf(textId) == -1){
                modelThemesToTexts[themeId].texts.push(textId)
            }

	    // Also store the reverse connection
	     if (!(textId in modelTextsToThemes)){
		 modelTextsToThemes[textId] = {"themes" : []};
	     }

	    if (modelTextsToThemes[textId].themes.indexOf(themeId) == -1){
		modelTextsToThemes[textId].themes.push(themeId)
	    }

        }
    }
    controllerDoPopulateThemes(true);
    controllerDoPopulateInterface();
}

function modelRenameTheme(themeId, newLabel){
    for (let i = 0; i < modelThemes.length; i++){
        if (modelThemes[i] == themeId){
            modelThemes[i].label = newLabel
        }
    }
    let updateThemeNameUrl = "update_theme_name";
    let data = {"theme_number": themeId, "theme_name" : newLabel, "analysis_id" : modelCurrentAnalysisVersionId}
    
    save_data(updateThemeNameUrl, doRenameTheme, data);
}

function doRenameTheme(res){
    // Nothing is done here (keeping empty method for debug purposes)
}

function getThemeName(themeId){
    for (let i = 0; i < modelThemes.length; i++){
        if (modelThemes[i] == themeId){
            return modelThemes[i].label
        }
    }
}

function deleteDatabaseTextThemeLink(themeId, textId){
    let deleteDatabaseTextThemeLinkUrl = "delete_theme_document_connection";
    let data = {"theme_number" : themeId, "document_id" : textId, "analysis_id" : modelCurrentAnalysisVersionId};
    
    save_data(deleteDatabaseTextThemeLinkUrl, doDeleteDatabaseTextThemeLink, data);
}

function doDeleteDatabaseTextThemeLink(res){
   // Nothing done here, only kept for debut reasons
}
////////
/// For loading data in the scroll list of previous models and analyses
///////

function modelLoadModelForSelectedDataSet(currentDataset){
    modelCurrentDataset = currentDataset;
    let modelForSelectedDataSetUrl = "get_all_models_for_collection_with_name";
    let data = {"collection_name" : currentDataset};
    
    get_data(modelForSelectedDataSetUrl, doLoadModelsForSelectedDataSet, data);
 
}

function doLoadModelsForSelectedDataSet(modelsForCurrentDatasetFromDataBase){
    resetModelData();
    resetModelChoiceData();
    
    for (let i = 0; i < modelsForCurrentDatasetFromDataBase.length; i++) {
        let m = modelsForCurrentDatasetFromDataBase[i];
        var  name_to_use = m["model_name"] + " " + m["date"];
        modelModelsForCurrentDataset.push({"value" : name_to_use, "id" : m["_id"]});
    }
    
    modelModelsForCurrentDataset.push({"value" : SELECTMODELTEXT, "id" : undefined});
    
    controllerDoPopulateInterface();
    controllerDoPopulateModelChoices(modelModelsForCurrentDataset);
}

///////
/// For constructing a new model
function modelConstructNewModel(modelName){
    let contructNewModelUrl = "make_model_for_collection";
    let data = {"collection_name" : modelCurrentDataset, "model_name" : modelName};
    save_data(contructNewModelUrl, modelLoadModelForCurrentDataSet, data);
}

// A dummy parameter, as the function that is submitted to get_data expects a parameter
function modelLoadModelForCurrentDataSet(dummy){
    modelLoadModelForSelectedDataSet(modelCurrentDataset)
}


///For loading the analyses-list
function modelLoadAnalysesForSelectedModel(newModelId){
    modelCurrentModelId = newModelId;
    let loadAnalysesUrl = "get_all_analyses_for_model";
    let data = {"model_id" : modelCurrentModelId};
    resetUserAnalysisData();
    
    get_data(loadAnalysesUrl, doLoadAnalysesForSelectedModel, data);
}

function doLoadAnalysesForSelectedModel(analysesForCurrentModelFromDataBase){
    resetAnalysisChoiceData();
    for (let i = 0; i < analysesForCurrentModelFromDataBase.length; i++) {
        let m = analysesForCurrentModelFromDataBase[i];
        modelAnalysesForCurrentModel.push({"value" : m["analysis_name"], "id" : m["_id"]});
    }
    
    modelAnalysesForCurrentModel.push({"value" : SELECTANALYSISTEXT, "id" : undefined});
    
    controllerDoPopulateAnalysisChoices(modelAnalysesForCurrentModel);
    resetUserAnalysisData();
    //controllerDoPopulateInterface();
}

function doLoadAnalysesForSelectedModelAndSelectOne(analysesForCurrentModelFromDataBase){
    doLoadAnalysesForSelectedModel(analysesForCurrentModelFromDataBase);
    controllerSelectChosenAnalysis(modelCurrentAnalysisName)
}


function modelLoadNewAnalysis(newAnalysisVersionId){
    resetUserAnalysisData();
    modelCurrentAnalysisVersionId = newAnalysisVersionId;
    
    getSavedTopicNames();
    getSavedUserDefinedLabels();
    getSavedThemes();
    

}

///////
/// For constructing a new analysis, loading analyses and exporting analysis
////////////
function modelConstructNewAnalysis(analysisName){
    let constructNewAnalysisUrl = "create_new_analysis";
    let data = {"model_id" : modelCurrentModelId, "analysis_name" : analysisName};
    save_data(constructNewAnalysisUrl, modelLoadAnalysisForCurrentModel, data);
}


function modelLoadAnalysisForCurrentModel(createdAnalysisParameters){

    let loadAnalysesUrl = "get_all_analyses_for_model";
    let data = {"model_id" : modelCurrentModelId};
    resetUserAnalysisData();
    
    modelCurrentAnalysisName = createdAnalysisParameters["analysis_name"];
    modelCurrentAnalysisVersionId = createdAnalysisParameters["analysis_id"];

    get_data(loadAnalysesUrl, doLoadAnalysesForSelectedModelAndSelectOne, data);
}

function modelExportAnalysis(){
    if (modelCurrentAnalysisVersionId == null){
	// Nothing to export if there is no analysis
	return;
    }
    let exportAnalysisUrl = "export_analysis";
    let data = {"analysis_id" : modelCurrentAnalysisVersionId};
    save_data(exportAnalysisUrl, doNotifyExportedAnalysis, data);
}

function doNotifyExportedAnalysis(savedData){
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
    
    save_data(updateUserLabelUrl, updateUserDefinedLabel, data);
}

function updateUserDefinedLabel(data){
    controllerDoPopulateOneTextElement(data);
    controllerDoPopulateThemes(false);
}

function getSavedUserDefinedLabels(){
    let savedUserDefinedLabels = "get_all_user_defined_labels";
    let data = {"analysis_id" : modelCurrentAnalysisVersionId};
    
    get_data(savedUserDefinedLabels, doGetUserDefinedLabels, data);
}

function doGetUserDefinedLabels(userLabels){
    for (let i = 0; i < userLabels.length; i++){
        modelUserTextLabels[userLabels[i].text_id] = userLabels[i].user_defined_label;
    }
    // The interface is updated with the labels from the call from update of themes
}

function modelResetRecentlyClickedForMachineLearningSorting(){
    modelMostRecentlyClickedText = undefined;
    modelThemeRankingForMostRecentlyClickedText = [];
}

