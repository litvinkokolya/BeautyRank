import {forwardRef, ForwardRefRenderFunction} from 'react';
import PhoneInput from 'react-phone-input-2';
import 'react-phone-input-2/lib/style.css';
import styles from './PhoneInput.module.scss';
import ru from 'react-phone-input-2/lang/ru.json';

interface InputProps {
    error?: string;
    onChange?: (value: string) => void;
    value?: string;
}

const supportedCountries = ['ru', 'kg', 'by', 'il'];

const PhoneInputBase: ForwardRefRenderFunction<
    HTMLInputElement,
    InputProps
> = ({error, onChange, value}) => {
    return (
        <>
      <span
          className={`${
              error ? styles.phone_input_error : styles.phone_input_error_hidden
          }`}
      >
        {error}
      </span>
            <PhoneInput
                autocompleteSearch
                inputClass={`${styles.phone_input} ${
                    error ? styles.phone_input_error : ''
                }`}
                containerClass={styles.phone_input_box}
                buttonClass={styles.phone_input_button}
                dropdownClass={styles.phone_input_dropdown}
                country={'ru'}
                onlyCountries={supportedCountries}
                onChange={onChange}
                value={value}
                countryCodeEditable={false}
                localization={ru}
            />
        </>
    );
};

export default forwardRef(PhoneInputBase);
