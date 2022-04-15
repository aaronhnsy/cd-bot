import "bootstrap";
import imagesLoaded from "imagesloaded";
import Masonry from "masonry-layout";

import "../css/app.scss";


const masonryGrids = document.querySelectorAll(".masonry");

masonryGrids.forEach(element => {
    const masonry = new Masonry(element, {
        percentPosition: true,
    });
    imagesLoaded(element, () => {
        masonry.layout();
    });
});
