// content.js
console.log("Content script runs if we are on reddit")

// Create hover overlay and add it to the page
$('<div id="mydiv"></div>').appendTo(document.body)
// Set the styles
$('#mydiv').css({
  position: "fixed",
  top: "120px",
  left: "0px",
  "z-index": 5,
  width: "4px",
  height: "100px",
  "min-height": "100px",
  "background-color": "rgb(106, 217, 134)",
  "border-radius": "0px 10px 10px 0px",
  padding: "3px"
})

// Check every second, as internal navigation in reddit doesn't always trigger a document reload
setInterval(function () {
  // JS regex to grab subreddit
  let check_subreddit = ""
  try {
    // Get the subreddit from the main window url
    let str = window.location.href;
    let result = str.match(/(\/r\/?.*?\/)/); // returns /r/yoursubreddit/
    let subreddit = result[0].slice(3, -1) // remove the /r/ and trailing slash off
    // console.log("Subreddit is " + subreddit);

    stats = ""
    // Check if subreddit has changed
    if (check_subreddit !== subreddit) {
      check_subreddit = subreddit;

      // Check if page is a supported subreddit
      subreddits = ["soccer", "baseball", "hockey", "mma", "running", "snowboarding", "climbing", "nba", "nfl", "politics", "casualuk", "news"]

      // Create links from list of subreddits
      function linkify(sub) {
        return `<a style="color:#037bfc;" href="https://reddit.com/r/${sub}" alt=${sub}>${sub}</a>`
      }

      // Function to create a list of links
      function list_to_links(subreddits) {
        let links = []
        subreddits.forEach(element => {
          links.push(linkify(element))
        });
        return links
      }
      // Create list
      sub_links = list_to_links(subreddits)

      // Inject the contents into the overlay
      if (subreddits.includes(subreddit.toLowerCase())) {
        // This url could be your S3 bucket as described in the notebook
        let url = "https://file-access-cvee2224cq-ew.a.run.app/artifacts/" + subreddit.toLowerCase() + ".png";
        stats = `<h1 style="padding: 10px;">Most talked about names in r/${subreddit} submission titles over the last week</h1><img src=${url} id="chart" style="max-width: 550px;"/><br>
        <p style="font-size=50%; max-width:500px;">Other subreddits with stats are: ${sub_links.join(", ")}</p>`;
      } else {
        stats = `<div style="max-width: 150px;"><h1 style="font-weight: bold;">Subreddit not currently supported</h1><br><br><p>Subreddits available are: ${sub_links.join(", ")}</p><div>`;
      }

      $("#mydiv").hover(function () {
          $(this).css({
            width: "auto",
            height: "auto",
          });
          // Add contents to container
          $(this).html(stats);
        },
        function () {
          $(this).css({
            width: "2px",
            height: "100px",
          });
          $(this).html('');
        });
    }
  } catch (error) {
    console.log("No subreddit found")
  }
}, 1000);