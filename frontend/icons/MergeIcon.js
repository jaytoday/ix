import React from "react";
import SVGIcon from "icons/SVGIcon";

export const MergeIcon = ({ ...props }) => {
  return (
    <SVGIcon transform="rotate(270deg)" {...props}>
      <path
        d="M 34.451172 14.640625 L 34.451172 51.921875 C 34.451172 65.156275 45.371861 76.027344 58.611328 76.027344 L 74.826172 76.027344 L 74.826172 122.48047 L 51.542969 122.48047 C 52.548279 123.66844 73.896271 148.94757 85.302734 162.36914 C 96.699189 148.94727 118.11464 123.6679 119.125 122.48047 L 95.841797 122.48047 L 95.841797 76.027344 L 112.05469 76.027344 C 125.28909 76.027344 136.2168 65.156142 136.2168 51.921875 L 136.2168 14.640625 L 120.48047 14.640625 L 120.48047 51.921875 C 120.48047 56.713608 116.84629 60.296875 112.05469 60.296875 L 58.617188 60.296875 C 53.825454 60.296875 50.189453 56.713475 50.189453 51.921875 L 50.189453 14.640625 L 34.451172 14.640625 z "
        transform="scale(0.75)"
      />
    </SVGIcon>
  );
};
