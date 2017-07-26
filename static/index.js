function setupWordCloud(frequencies) {
  var setScale = function (element, scale){
    element.style.transform = "scale(" + scale + ")";
  };
  var options =
  {
    rotateRatio: 0,
    list : frequencies,
    gridSize: Math.round(16 * $("#chart").width() / 1024),
    weightFactor: function (size) {
      return Math.pow(size, 1.9) * $("#chart").width() / 1024;
    },
    hover: function(item, dim, event, spans){
      if(spans)
        setScale(spans[0], 1.5);
    },
    hoverRelease: function(spans) {
      if(spans)
        setScale(spans[0], 1);
    },
    click: function(item) {
      var clickedWord = item[0];
      $("#search-query").val(clickedWord);
      $("#search-query-form").submit();
    }
  };
  WordCloud(document.getElementById('chart'), options);

  function onWordCloudStop(){
    var elements = $("#chart").find("span");
    elements.css("transition", "transform 0.3s ease-out");
    elements.css("cursor", "pointer");
  }

  // element creation is delayed so I need to wait for the wordcloudstop event
  document.getElementById('chart').addEventListener('wordcloudstop', onWordCloudStop)
}

Array.max = function(array){
  return Math.max.apply(Math, array);
};

Array.min = function(array){
  return Math.min.apply(Math, array);
};

function getValues(object){
  var values = [];
  for(var i in object)
    values = values.concat(object[i][1]);
  return values;
}

function capWeights(weights){
  var values = getValues(weights);
  var valueMin = Array.min(values);
  var valueMax = Array.max(values);
  var valueSpread = valueMax - valueMin;
  var cappedWeights = [];
  // capRangeの最小値が3以下だとIssue #14が発生する
  var capRange = [4, 10];
  var capMin = capRange[0];
  var capSpread = capRange[1] - capRange[0];
  for(var i in weights){
    var w = weights[i];
    var k = w[0];
    var v = w[1];
    var fraction = 0.5;
    if(valueSpread)
      fraction = (v - valueMin) / valueSpread;
    v = capMin + (capSpread * fraction);
    cappedWeights = cappedWeights.concat([[k, v]])
  }
  return cappedWeights;
}

function getBeginningOfToday(){
  var d = new Date();
  d.setHours(0);
  d.setMinutes(0);
  d.setSeconds(0);
  d.setMilliseconds(0);
  return d;
}

function getBeginningOfThisMonth(){
  var d = getBeginningOfToday();
  d.setDate(1);
  return d;
}

function prepareTimestamp(timestamp){
  function n(n){
      return n > 9 ? "" + n: "0" + n;
  }

  var result = "";

  var dateOfTweet = new Date(0);
  dateOfTweet.setUTCSeconds(timestamp);

  if (dateOfTweet < getBeginningOfThisMonth())
    result += (dateOfTweet.getMonth() + 1) + '月';

  if (dateOfTweet < getBeginningOfToday())
    result += dateOfTweet.getDate() + '日';

  result += n(dateOfTweet.getHours()) + ':' + n(dateOfTweet.getMinutes());
  return result;
}

function setupSearch(){
  function createSearchResultNode(datum){
    var node = $("#search-result-template").find("#search-result-row").clone();
    node.find("#search-result-date").text(prepareTimestamp(datum.created_at));
    node.find("#search-result-user").text(datum.user);
    node.find("#search-result-tweet").text(datum.text);
    return node;
  }

  var searchView = $("#search-view");
  var searchViewLoadingWrapper = $("#search-view-loading-wrapper");

  function hideLoading(){
    searchView.removeClass("hidden");
    searchViewLoadingWrapper.addClass("hidden");
  }

  function showLoading(){
    searchView.addClass("hidden");
    searchViewLoadingWrapper.removeClass("hidden");
  }

  function populateSearchResults(data){
    hideLoading();
    searchView.empty();
    for(var i in data)
        searchView.append(createSearchResultNode(data[i]));
  }

  var ajaxRequest = null;

  function initQuery(data){
    if(ajaxRequest)
      ajaxRequest.abort();
    ajaxRequest = new window.XMLHttpRequest();
    $.ajax({
      // The returned object of $.ajax does not have the xhr property in jQuery3
      xhr: function(){return ajaxRequest;},
      dataType: "json",
      type: "POST",
      url: "search",
      data: data,
      success: populateSearchResults
    });
    showLoading();
  }

  var searchQueryForm = $("#search-query-form");
  searchQueryForm.submit(function(e) {
    $('#modal').modal('show');
    $("#modal-search-query").val($("#search-query").val());
    initQuery($(this).serialize());
    e.preventDefault();
  });

  var modalSearchQueryForm = $("#modal-search-query-form");
  modalSearchQueryForm.submit(function(e) {
    initQuery($(this).serialize());
    e.preventDefault();
  });
}

function onLoad(weights){
  setupWordCloud(capWeights(weights));
  setupSearch();
}
