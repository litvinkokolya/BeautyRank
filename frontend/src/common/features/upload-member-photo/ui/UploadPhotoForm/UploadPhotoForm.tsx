import {Button} from 'common/shared/ui/button';
import {useState} from 'react';
import styles from './UploadPhotoForm.module.scss';
import {useRouter} from 'next/router';
import UploadPhotoBox from '../UploadPhotoBox/UploadPhotoBox';
import {
    useUploadPhotos,
    useMemberImageSrc,
    useFileChange,
    useMember,
} from 'common/features/upload-member-photo/model';
import {Loader} from 'common/shared/ui/loader';
import Link from 'next/link';
import {BEAUTY_RANK_BOT} from 'common/shared/api/endpoints';

const UploadPhotoForm = () => {
    const router = useRouter();
    const memberId = Number(router.query.memberId);

    const {member, selectedFiles, setSelectedFiles} = useMember(memberId);
    const {handleFileChange} = useFileChange({
        member,
        memberId,
        selectedFiles,
        setSelectedFiles,
    });
    const {getImageSrc} = useMemberImageSrc({selectedFiles});
    const {mutation, isLoading} = useUploadPhotos({selectedFiles});

    const buttonIsDisabled = () => {
        if (selectedFiles.length) {
            return selectedFiles.some(
                (file) => file?.photo === undefined || file?.photo === null
            );
        }
        return true;
    };

    return (
        <>
            {member ? (
                <>
                    <div className={styles.upload_photo__decor}></div>
                    <h3 className={styles.upload_photo__title}>Загрузите фото модели</h3>
                    <p className={styles.upload_photo__nomination}>
                        {member?.nomination} {member?.category}
                    </p>
                    <form className={styles.upload_photo__form}>
                        <UploadPhotoBox
                            title="ДО"
                            photos={member?.nomination_info.after || []}
                            onChange={handleFileChange}
                            getImageSrc={getImageSrc}
                        />
                        <UploadPhotoBox
                            title="ПОСЛЕ"
                            photos={member?.nomination_info.before || []}
                            onChange={(index) =>
                                handleFileChange(
                                    index + (member?.nomination_info.after.length || 0)
                                )
                            }
                            getImageSrc={(index) =>
                                getImageSrc(index + (member?.nomination_info.after.length || 0))
                            }
                        />
                    </form>
                    {/*<Link*/}
                    {/*  target="_blank"*/}
                    {/*  href={`${BEAUTY_RANK_BOT}${memberId}`}*/}
                    {/*  className={styles.upload_photo__video_link}*/}
                    {/*>*/}
                    {/*  Загрузить Видео*/}
                    {/*</Link>*/}
                    <Button
                        disabled={buttonIsDisabled() || isLoading}
                        className={styles.upload_photo__btn}
                        onClick={() => mutation.mutate()}
                    >
                        {isLoading ? 'Загрузка...' : 'Подтвердить'}
                    </Button>
                </>
            ) : (
                <Loader fullPage/>
            )}
        </>
    );
};

export default UploadPhotoForm;
