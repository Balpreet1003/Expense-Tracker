import React, { useRef, useState, useEffect } from 'react';
import { LuUser, LuUpload, LuTrash, LuPencil } from 'react-icons/lu';

const sizeClasses = {
    default: {
        wrapper: 'w-20 h-20',
        icon: 'text-4xl',
        actionButton: 'w-8 h-8',
        image: 'w-20 h-20',
    },
    xl: {
        wrapper: 'w-28 h-28 sm:w-32 sm:h-32 md:w-36 md:h-36',
        icon: 'text-5xl sm:text-6xl',
        actionButton: 'w-10 h-10 sm:w-11 sm:h-11',
        image: 'w-28 h-28 sm:w-32 sm:h-32 md:w-36 md:h-36',
    },
};

const ProfilePhotoSelector = ({ image, setImage, size = 'default' }) => {
    const inputRef = useRef(null);
    const [previewUrl, setPreview] = useState(null);
    const [isPopupOpen, setIsPopupOpen] = useState(false);
    const objectUrlRef = useRef(null);
    const selectedSize = sizeClasses[size] || sizeClasses.default;

    const handleImageChange = (event) => {
        const file = event.target.files[0];
        if (file) {
            setImage(file);
            setIsPopupOpen(false);
        }

        event.target.value = '';
    };

    const handleRemoveImage = () => {
        setImage(null);
        setPreview(null);
        setIsPopupOpen(false);
        if (objectUrlRef.current) {
            URL.revokeObjectURL(objectUrlRef.current);
            objectUrlRef.current = null;
        }
    };

    const onChooseFile = () => {
        inputRef.current.click();
    };

    useEffect(() => {
        if (objectUrlRef.current) {
            URL.revokeObjectURL(objectUrlRef.current);
            objectUrlRef.current = null;
        }

        if (!image) {
            setPreview(null);
            return undefined;
        }

        if (typeof image === 'string') {
            setPreview(image);
            return undefined;
        }

        if (image instanceof File || image instanceof Blob) {
            const url = URL.createObjectURL(image);
            objectUrlRef.current = url;
            setPreview(url);
            return undefined;
        }

        setPreview(null);
        return undefined;
    }, [image]);

    useEffect(() => () => {
        if (objectUrlRef.current) {
            URL.revokeObjectURL(objectUrlRef.current);
        }
    }, []);

    return (
        <div className='flex justify-center mb-6'>
            <input
                type="file"
                accept="image/*"
                ref={inputRef}
                onChange={handleImageChange}
                className='hidden'
            />

            <div className='relative'>
                {!image ? (
                    <div className={`flex items-center justify-center bg-purple-100 rounded-full ${selectedSize.wrapper}`}>
                        <LuUser className={`${selectedSize.icon} text-primary`} />
                    </div>
                ) : (
                    <img
                        src={previewUrl}
                        alt='profile photo'
                        className={`rounded-full object-cover ${selectedSize.image}`}
                    />
                )}

                <button
                    type='button'
                    className={`flex items-center justify-center bg-[#875cf5] text-white rounded-full absolute -bottom-1 -right-1 shadow-md ${selectedSize.actionButton}`}
                    onClick={() => setIsPopupOpen(true)}
                    aria-label='Edit profile photo'
                >
                    <LuPencil />
                </button>
            </div>

            {isPopupOpen && (
                <div className='fixed inset-0 z-50 flex items-center justify-center bg-black/45 px-4 py-6'>
                    <div className='w-full max-w-md rounded-2xl bg-white p-4 sm:p-6 shadow-xl'>
                        <div className='flex justify-end'>
                            <button
                                type='button'
                                className='text-slate-500 hover:text-slate-800 text-sm font-semibold'
                                onClick={() => setIsPopupOpen(false)}
                            >
                                Close
                            </button>
                        </div>

                        {!previewUrl ? (
                            <button
                                type='button'
                                onClick={onChooseFile}
                                className='mt-2 flex h-56 w-full flex-col items-center justify-center rounded-xl border-2 border-dashed border-purple-200 bg-purple-50 text-primary transition-colors hover:bg-purple-100 sm:h-64'
                            >
                                <LuUpload className='text-4xl sm:text-5xl' />
                                <span className='mt-3 text-sm font-semibold sm:text-base'>Upload Photo</span>
                            </button>
                        ) : (
                            <>
                                <div className='mt-2 flex h-56 w-full items-center justify-center rounded-xl bg-slate-50 sm:h-64'>
                                    <img
                                        src={previewUrl}
                                        alt='profile preview'
                                        className='h-full w-full rounded-xl object-cover'
                                    />
                                </div>

                                <div className='mt-4 grid grid-cols-2 gap-3'>
                                    <button
                                        type='button'
                                        onClick={onChooseFile}
                                        className='flex h-11 items-center justify-center gap-2 rounded-lg bg-[#875cf5] text-sm font-semibold text-white transition-colors hover:bg-[#7449e7]'
                                    >
                                        <LuUpload />
                                        Upload
                                    </button>

                                    <button
                                        type='button'
                                        onClick={handleRemoveImage}
                                        className='flex h-11 items-center justify-center gap-2 rounded-lg bg-red-500 text-sm font-semibold text-white transition-colors hover:bg-red-600'
                                    >
                                        <LuTrash />
                                        Delete
                                    </button>
                                </div>
                            </>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default ProfilePhotoSelector;
