import React from "react";

const DropDown = ({option, options, setOption, text}) => {
    // console.log(options)
    const selectOption = (event) =>{
        setOption(event.target.value);
    }
    return(
        <select value={option} onChange={selectOption}>
                {options.map((option) => (
                <option value={option}>{text}: {option}</option>
            ))}

            </select>
    );
}

export default DropDown