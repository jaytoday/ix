import React from "react";
import SVGIcon from "icons/SVGIcon";

export const SplitIcon = ({ ...props }) => {
  return (
    <SVGIcon transform="rotate(90deg)" {...props}>
      <path d="m31.719 8.6016c-8.5547 10.066-24.566 29.027-25.32 29.918h19.441v27.961c0 9.9258 8.1914 18.078 18.121 18.078h12.16v34.84h15.762v-34.84h12.16c9.9258 0 18.121-8.1523 18.121-18.078v-27.961h19.441c-0.75781-0.89062-16.809-19.852-25.367-29.918-8.5547 10.066-24.566 29.027-25.316 29.918h19.441v27.961c0 3.5938-2.7266 6.2812-6.3203 6.2812h-40.078c-3.5938 0-6.3203-2.6875-6.3203-6.2812v-27.961h19.441c-0.75781-0.89062-16.82-19.852-25.367-29.918z" />
    </SVGIcon>
  );
};
