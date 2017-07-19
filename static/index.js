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
        $.scrollTo($("#search-query-container"), 500);
        var clickedWord = item[0];
        $("#search-query").val(clickedWord);
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
