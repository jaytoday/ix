import React, { useContext, useEffect } from "react";
import { NodeTypeSearch } from "chains/editor/NodeTypeSearch";
import {
  Box,
  Popover,
  PopoverArrow,
  PopoverCloseButton,
  PopoverContent,
  PopoverHeader,
  PopoverTrigger,
  useDisclosure,
} from "@chakra-ui/react";
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faSquarePlus } from "@fortawesome/free-solid-svg-icons";
import { useColorMode } from "@chakra-ui/color-mode";
import { SelectedNodeContext } from "chains/editor/contexts";
import { NO_SCROLLBAR_CSS } from "site/css";
import { MenuItem } from "site/MenuItem";
import { useLeftSidebarContext } from "site/sidebar/context";

export const NodeTypeSearchButton = () => {
  const { isOpen, onToggle, onClose, onOpen } = useDisclosure();
  const initialFocusRef = React.useRef();

  // auto-open when connector is [de]selected
  // HAX: couldn't get this to work when closeOnBlur={true}
  //      this behavior is mostly ok though so can revisit later
  //      to make popover pinning a toggle.
  const { selectedConnector } = useContext(SelectedNodeContext);
  useEffect(() => {
    if (selectedConnector && !isOpen) {
      onOpen();
    } else if (!selectedConnector) {
      onClose();
    }
  }, [selectedConnector]);

  const { colorMode } = useColorMode();
  const highlightColor = colorMode === "light" ? "blue.500" : "blue.400";
  const color = colorMode === "light" ? "gray.800" : "white";

  const sideBar = useLeftSidebarContext();
  const width = sideBar.size === "icons" ? "25px" : "110px";

  // HAX: Popover must be closedOnBlue=False to allow for connectors to
  //      switch without closing the popover. It proved very difficult to
  //      prevent onClose from detecting that a new connector was selected.
  return (
    <Popover
      isOpen={isOpen}
      onClose={onClose}
      placement={"right-start"}
      closeOnBlur={false}
      initialFocusRef={initialFocusRef}
    >
      <PopoverTrigger>
        <Box
          onClick={onToggle}
          width={width}
          transition="width 0.3s ease-out, max-width 0.3s ease-out"
        >
          <MenuItem onClick={onToggle} title={"Add Node"}>
            <FontAwesomeIcon size={"lg"} icon={faSquarePlus} />
          </MenuItem>
        </Box>
      </PopoverTrigger>
      <PopoverContent
        zIndex={99998}
        pb={2}
        boxShadow="0px 0px 10px 0px rgba(0,0,0,0.15)"
        css={NO_SCROLLBAR_CSS}
      >
        <PopoverHeader
          borderBottom="2px solid"
          borderColor={highlightColor}
          color={color}
        >
          Components
        </PopoverHeader>
        <PopoverArrow />
        <PopoverCloseButton />
        <NodeTypeSearch initialFocusRef={initialFocusRef} />
      </PopoverContent>
    </Popover>
  );
};
