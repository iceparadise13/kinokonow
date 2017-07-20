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
        $.scrollTo($("#search-query-row"), 500);
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

function onLoad(frequencies){
    setupWordCloud(frequencies);

    function populateSearchResults(data){
      var searchView = $("#search-view");
      searchView.empty();
      for(var i =0; i<data.length; ++i){
          var row = data[i];
          var node = $("#search-result-template").find("#search-result-row").clone();
          node.find("#search-result-user").text(row.user);
          node.find("#search-result-tweet").text(row.text);
          searchView.append(node);
      }
    }

    $("#search-query-form").submit(function(e) {
        $.ajax({
               dataType: "json",
               type: "POST",
               url: "search",
               data: $("#search-query-form").serialize(),
               success: populateSearchResults
             });
        e.preventDefault();
    });
}
